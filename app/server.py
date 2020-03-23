import aiohttp
import asyncio
import uvicorn
from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

export_file_url = 'https://drive.google.com/uc?export=download&id=1CL6X0azxL1LjQf-xq5aMP4Akp2xyjxCV'
export_file_name = 'export.pkl'

classes = ['Affenpinscher',
 'Afghan_hound',
 'African_hunting_dog',
 'Airedale',
 'American_Staffordshire_terrier',
 'Appenzeller',
 'Australian_terrier',
 'Basenji',
 'Basset',
 'Beagle',
 'Bedlington_terrier',
 'Bernese_mountain_dog',
 'Black-and-tan_coonhound',
 'Blenheim_spaniel',
 'Bloodhound',
 'Bluetick',
 'Border_collie',
 'Border_terrier',
 'Borzoi',
 'Boston_bull',
 'Bouvier_des_Flandres',
 'Boxer',
 'Brabancon_griffon',
 'Briard',
 'Brittany_spaniel',
 'Bull_mastiff',
 'Cairn',
 'Cardigan',
 'Chesapeake_Bay_retriever',
 'Chihuahua',
 'Chow',
 'Clumber',
 'Cocker_spaniel',
 'Collie',
 'Curly-coated_retriever',
 'Dandie_Dinmont',
 'Dhole',
 'Dingo',
 'Doberman',
 'English_foxhound',
 'English_setter',
 'English_springer',
 'EntleBucher',
 'Eskimo_dog',
 'Flat-coated_retriever',
 'French_bulldog',
 'German_shepherd',
 'German_short-haired_pointer',
 'Giant_schnauzer',
 'Golden_retriever',
 'Gordon_setter',
 'Great_Dane',
 'Great_Pyrenees',
 'Greater_Swiss_Mountain_dog',
 'Groenendael',
 'Ibizan_hound',
 'Irish_setter',
 'Irish_terrier',
 'Irish_water_spaniel',
 'Irish_wolfhound',
 'Italian_greyhound',
 'Japanese_spaniel',
 'Keeshond',
 'Kelpie',
 'Kerry_blue_terrier',
 'Komondor',
 'Labrador_retriever',
 'Lakeland_terrier',
 'Leonberg',
 'Lhasa',
 'Malamute',
 'Malinois',
 'Maltese_dog',
 'Mexican_hairless',
 'Miniature_pinscher',
 'Miniature_poodle',
 'Miniature_schnauzer',
 'Newfoundland',
 'Norfolk_terrier',
 'Norwegian_elkhound',
 'Norwich_terrier',
 'Not_sure_Get_a_better_image_of_dog',
 'Old_English_sheepdog',
 'Otterhound',
 'Papillon',
 'Pekinese',
 'Pembroke',
 'Pomeranian',
 'Pug',
 'Rhodesian_ridgeback',
 'Rottweiler',
 'Saint_Bernard',
 'Saluki',
 'Samoyed',
 'Schipperke',
 'Scotch_terrier',
 'Scottish_deerhound',
 'Sealyham_terrier',
 'Shetland_sheepdog',
 'Shih-Tzu',
 'Siberian_husky',
 'Silky_terrier',
 'Soft-coated_wheaten_terrier',
 'Staffordshire_bullterrier',
 'Standard_poodle',
 'Standard_schnauzer',
 'Sussex_spaniel',
 'Tibetan_mastiff',
 'Tibetan_terrier',
 'Toy_poodle',
 'Toy_terrier',
 'Vizsla',
 'Walker_hound',
 'Weimaraner',
 'Welsh_springer_spaniel',
 'West_Highland_white_terrier',
 'Whippet',
 'Wire-haired_fox_terrier',
 'Yorkshire_terrier',
 'kuvasz',
 'redbone']

path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    await download_file(export_file_url, path / export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())


@app.route('/analyze', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    img_bytes = await (img_data['file'].read())
    img = open_image(BytesIO(img_bytes))
    #prediction = learn.predict(img)[0]
    preds, idx, output = learn.predict(img)
    d = dict({learn.data.classes[i]: round(to_np(p)*100,2) for i, p in enumerate(output) if p > 0.2})
    return JSONResponse({'result': str(d)})


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
