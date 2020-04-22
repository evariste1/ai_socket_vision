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

export_file_url = 'https://drive.google.com/uc?export=download&id=1qcKgrfnV0OAYTwkd1_u3jdvlReYs7_LU'
export_file_name = 'export.pkl'

classes = ['COVID-19 INFECTION', 'NO INFECTION', 'NOT CERTAIN', 'PNEUMONIA INFECTION']
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
    d = dict({learn.data.classes[i]: round(to_np(p)*100,2) for i, p in enumerate(output) if p > 0.45})
    outcome=str(d)
    outcome=outcome.strip('{}\'')
    
    #pie chart code-start
    import matplotlib.pyplot as plt
    keys = d.keys()
    values = d.values()
    color_list=[]
    color_dict={'NOT CERTAIN':'red','COVID-19 INFECTION':'lightcoral','PNEUMONIA INFECTION':'khaki','NO INFECTION':'lime'}
    for key in d:
        new_color=color_dict[key]
        color_list.append(new_color)
    plt.pie(values,labels=keys, colors=color_list, startangle=90, shadow=True, autopct='%1.2f%%')
    plt.title('Diagnosis')
    plt.axis('equal')
    plt.show()
    #pie chart code -end
    
    return JSONResponse(d)


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
