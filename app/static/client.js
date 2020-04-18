/*
window.onload = function() {

var dataPoints = [];
var myObj, x;
myObj = {"Not certain":"60", "COVID-19":"30", "Pneumonia":"20"};//replace with jsondata
for (x in myObj) {
dataPoints.push({
			y: parseFloat(myObj[x]),
			label: x 
		});
  }


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

*/


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

function analyze() {
  var uploadFiles = el("file-input").files;
  if (uploadFiles.length !== 1) alert("Please select a file to analyze!");

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
	    alert(JSON.stringify(response));
     // el("result-label").innerHTML = `Diagnosis & Confidence Level(%)= ${response["result"]}`;
	  
	  //new code for pie chart
	  
		var dataPoints = [];
		var x;
		for (x in response) {
		dataPoints.push({
					y: parseFloat(response[x]),
					label: x 
				});
		  }
	    alert(JSON.stringify(dataPoints));
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


