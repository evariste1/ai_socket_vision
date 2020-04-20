/* window.onload = function() {

var dataPoints = [];
var myObj, x;
myObj = {"Not certain":"60", "COVID-19":"30", "Pneumonia":"18", "no infection":"2"};//replace with jsondata
for (x in myObj) {
if(x=="Not certain"){var color="#e3dbf9";}
else if(x=="COVID-19"){var color="#ff5900";}
else if(x=="Pneumonia"){var color="#e3e567";}
else {var color="#74fa00";}
dataPoints.push({
			y: parseFloat(myObj[x]),
			label: x,
			color: color
		});
  }

 */
var chart = new CanvasJS.Chart("chartContainer", {
	animationEnabled: true,
	title: {
		text: "Prediction"
	},
	data: [{
		type: "pie",
		startAngle: 240,
		yValueFormatString: "##0.00\"%\"",
		indexLabel: "{label} {y}",
		dataPoints: dataPoints
	}]
});
chart.render();



}  
var el = x => document.getElementById(x);

function showPicker() {
  el("file-input").click();
}

function showPicked(input) {
  el("upload-label").innerHTML = input.files[0].name;
  var reader = new FileReader();
  reader.onload = function(e) {
    el("image-picked").src = e.target.result;
    el("image-picked").className = "";
  };
  reader.readAsDataURL(input.files[0]);
}

function hasExtension(inputID, exts) {
    var fileName = el(inputID).value;
  	return (new RegExp('(' + exts.join('|').replace(/\./g, '\\.') + ')$', "i")).test(fileName);
}

function analyze() {
  var uploadFiles = el("file-input").files;
  if (uploadFiles.length !== 1) {
	  alert("Please select a file to analyze!");
	  return false;}

 if (!hasExtension('file-input', ['.jpg', '.jpeg','.gif', '.png'])) {
   	alert("select image file!");
	el("upload-label").innerHTML = "No file chosen";
	 el("image-picked").src = "";
    el("image-picked").className = "no-display";
	return false;
}

  el("analyze-button").innerHTML = "Analyzing...";
  var xhr = new XMLHttpRequest();
  var loc = window.location;
  xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`,
    true);
  xhr.onerror = function() {
    alert(xhr.responseText);
  };
  xhr.onload = function(e) {
	  
    if (this.readyState === 4) {
      var response = JSON.parse(e.target.responseText);
	    //alert(JSON.stringify(response));
     // el("result-label").innerHTML = `Diagnosis & Confidence Level(%)= ${response["result"]}`;
	  
	  //new code for pie chart
	  
		var dataPoints = [];
		var x;
		for (x in response) {
		//if there is change in class name in python change here also
			if(x=="NOT CERTAIN"){var color="#e3dbf9";}
			else if(x=="COVID-19 INFECTION"){var color="#ff5900";}
			else if(x=="PNEUMONIA INFECTION"){var color="#e3e567";}
			else {var color="#74fa00";}
			dataPoints.push({
					y: parseFloat(response[x]),
					label: x,
					color: color
				});
		  }
	    //alert(JSON.stringify(dataPoints));
		// creating the pie chart to be displayed in chartContainer div using the data cretaed in datapoint above
		var chart = new CanvasJS.Chart("chartContainer", {
			animationEnabled: true,
			title: {
				text: "Prediction"
			},
			data: [{
				type: "pie",
				startAngle: 240,
				yValueFormatString: "##0.00\"%\"",
				indexLabel: "{label} {y}",
				dataPoints: dataPoints
			}]
		});
		chart.render();

	  
	  //end of pie chart
	  
	  
	  
	  
	  
    }
    el("analyze-button").innerHTML = "Analyze";
  };

  var fileData = new FormData();
  fileData.append("file", uploadFiles[0]);
  xhr.send(fileData);
}
