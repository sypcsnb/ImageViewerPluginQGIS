'use strict';

// Create viewer.
var viewer = new Marzipano.Viewer(document.getElementById('pano'));

// Create source.
var source = Marzipano.ImageUrlSource.fromString(
  "image.jpg"
);
console.log(Marzipano.ImageUrlSource);
// Create geometry.
var geometry = new Marzipano.EquirectGeometry([{ width: 8192 }]);

// Create view.
var limiter = Marzipano.RectilinearView.limit.traditional(8192, 100*Math.PI/180); //ขอบเขตในการมองเห็น
var view = new Marzipano.RectilinearView({ yaw:Math.PI/180 },limiter);

// Create scene.
var scene = viewer.createScene({
  source: source,
  geometry: geometry,
  view: view,
  pinFirstLevel: true
});

// Display scene.
scene.switchTo({
    transitionDuration: 0
});

var viewChangeHandler = function() {
    var yaw = view.yaw();
	var d_yaw=yaw/(Math.PI/180)
	console.log(d_yaw);
  };
 
view.addEventListener('change', viewChangeHandler);

var autorotate = Marzipano.autorotate({
  yawSpeed: 0.1,         // Yaw rotation speed
  targetPitch: 0,        // Pitch value to converge to
  targetFov: Math.PI/2   // Fov value to converge to
});


var cone = {
    img: "img/cone.png"
};
var trafficLight = {
    img: "img/traffic_light.png"
};
var trafficSigns = {
    img: "img/stop_sign.png"
};

var rawFile = new XMLHttpRequest();
rawFile.open("GET", "img_tmp.txt", false);
rawFile.onreadystatechange = function ()
{
    if(rawFile.readyState === 4)
    {
        if(rawFile.status === 200 || rawFile.status == 0)
        {
            window.allText = rawFile.responseText;
            console.log(allText);
        }
    }
}
rawFile.send(null);

var rawFile = new XMLHttpRequest();
rawFile.open("GET", "gps_tmp.txt", false);
rawFile.onreadystatechange = function ()
{
    if(rawFile.readyState === 4)
    {
        if(rawFile.status === 200 || rawFile.status == 0)
        {
            window.allText3 = rawFile.responseText;
            console.log(allText3);
        }
    }
}
rawFile.send(null);

//create obj when open added file
window.checkAdd = false;
var rawFile2 = new XMLHttpRequest();
rawFile2.open("GET", "./project/"+allText+".txt" , false);
rawFile2.onreadystatechange = function ()
{
    if(rawFile2.readyState === 4)
    {
        if(rawFile2.status === 200 || rawFile2.status == 0)
        {
            checkAdd = true;
            window.allText5 = rawFile2.responseText.split("\n" && " ");
            window.allText2 = rawFile2.responseText;
            var j = 0;
            console.log(allText2);
            window.allText4 = new Array ( );
            for (var i = 0 ; i < allText5.length-3 ; i++){
                allText4[i] = allText5[i+3];
            }
               
            console.log(allText4);

            for (var i = 1 ; i < allText4.length ; i += 3) {
                if (allText4[j] == "\nCone") {
                    var imgCone = document.createElement('img');
                    imgCone.src = cone.img;
                    var position_contextmenu = { yaw: allText4[j+1]*Math.PI/180, pitch: allText4[j+2]*Math.PI/180};
                    scene.hotspotContainer().createHotspot(imgCone, position_contextmenu);
                    j += 3;
                }
                if (allText4[j] == "\nTrafficLight") {
                    var imgTL = document.createElement('img');
                    imgTL.src = trafficLight.img;
                    var position_contextmenu = { yaw: allText4[j+1]*Math.PI/180, pitch: allText4[j+2]*Math.PI/180};
                    scene.hotspotContainer().createHotspot(imgTL, position_contextmenu);
                    j += 3;
                   
                }
                if (allText4[j] == "\nTrafficSign") {
                    var imgTS = document.createElement('img');
                    imgTS.src = trafficSigns.img;
                    var position_contextmenu = { yaw: allText4[j+1]*Math.PI/180, pitch: allText4[j+2]*Math.PI/180};
                    scene.hotspotContainer().createHotspot(imgTS, position_contextmenu);
                    j += 3;
                }
            }
        }
    }
}
rawFile2.send(null);
//console.log(rawFile2);


document.querySelector("#save").addEventListener('click', exportObj);

function exportObj() {
    window.objTxt = new Array ( );
    if (coneListYaw.length != 0) {
        for (var i = 1 ; i < coneListYaw.length ; i++){
            if (coneListYaw[i] < 0) {
                objTxt[objTxt.length+1] = new Array ("Cone", coneListYaw[i]*(180/Math.PI)+360, coneListPitch[i]*(90/Math.PI));
            }else{
                objTxt[objTxt.length+1] = new Array ("Cone", coneListYaw[i]*(180/Math.PI), coneListPitch[i]*(90/Math.PI));
            }
        }
    }
    if (tlListYaw.length != 0) {
        for (var i = 1 ; i < tlListYaw.length ; i++){
            if (tlListYaw[i] < 0) {
                objTxt[objTxt.length+1] = new Array ("TrafficLight", tlListYaw[i]*(180/Math.PI)+360, tlListPitch[i]*(90/Math.PI));
            }else{
                objTxt[objTxt.length+1] = new Array ("TrafficLight", tlListYaw[i]*(180/Math.PI), tlListPitch[i]*(90/Math.PI));
            }
        }
    }
    if (tsListYaw.length != 0) {
        for (var i = 1 ; i < tsListYaw.length ; i++){
            if (tsListYaw[i] < 0) {
                objTxt[objTxt.length+1] = new Array ("TrafficSign", tsListYaw[i]*(180/Math.PI)+360, tsListPitch[i]*(90/Math.PI));
            }else{
                objTxt[objTxt.length+1] = new Array ("TrafficSign", tsListYaw[i]*(180/Math.PI), tsListPitch[i]*(90/Math.PI));
            }
        }
    }

    if (checkAdd == false) {
        var content = [];
        content = allText+" "+allText3+"\n";
        objTxt.forEach(function(row, index) {
            content += row.join(" ") + " \n";
        });
        var blob = new Blob([content], {type: "text/plain;charset=utf-8"});
        window.saveAs(blob, allText+"_add.txt");	
    }else{
        var content = [];
        content = allText2;
        objTxt.forEach(function(row, index) {
            content += row.join(" ")+ " \n";
        });
        var blob = new Blob([content], {type: "text/plain;charset=utf-8"});
        window.saveAs(blob, allText+".txt");	
    }
    
}

var createConeFlag = 0;
var createTlFlag = 0;
var createTsFlag = 0;

window.coneListYaw = [];
window.coneListPitch = [];
window.tlListYaw = [];
window.tlListPitch = [];
window.tsListYaw = [];
window.tsListPitch = [];

function createCone() {
    var imgCone = document.createElement('img');
    imgCone.src = cone.img;
    var position_contextmenu = { yaw: loc_contextmenu.yaw, pitch: loc_contextmenu.pitch};
    scene.hotspotContainer().createHotspot(imgCone, position_contextmenu);
    createConeFlag = createConeFlag + 1;
    coneListYaw[createConeFlag] = position_contextmenu.yaw;
    coneListPitch[createConeFlag] = position_contextmenu.pitch;    
    imgCone.addEventListener("mousedown", function mousedown (e1) {
        viewer.controls().disable();

        var event = function (e2) {
            var view = scene.view();
            var loc2  = view.screenToCoordinates({x : e2.clientX, y: e2.clientY});
            var position3 = { yaw: loc2.yaw, pitch: loc2.pitch};
            scene.hotspotContainer().createHotspot(imgCone, position3);
        };
        pano.addEventListener("mousemove", event, false);

         pano.addEventListener("mouseup", function mouseup (e3) {
                pano.removeEventListener("mousemove", event, false);
                var loc3  = view.screenToCoordinates({x : e3.clientX, y: e3.clientY});
                var position4 = { yaw: loc3.yaw, pitch: loc3.pitch};
                scene.hotspotContainer().createHotspot(imgCone, position4);
                pano.removeEventListener("mousedown", mousedown);
                pano.removeEventListener("mouseup", mouseup);
                viewer.controls().enable();
                coneListYaw[createConeFlag] = loc3.yaw;
                coneListPitch[createConeFlag] = loc3.pitch;
         })
    })
}


function createTL() {
    var imgTL = document.createElement('img');
    imgTL.src = trafficLight.img;
    var position_contextmenu = { yaw: loc_contextmenu.yaw, pitch: loc_contextmenu.pitch};
    scene.hotspotContainer().createHotspot(imgTL, position_contextmenu);
    createTlFlag = createTlFlag + 1;
    tlListYaw[createTlFlag] = position_contextmenu.yaw;
    tlListPitch[createTlFlag] = position_contextmenu.pitch;   
    imgTL.addEventListener("mousedown", function mousedown (e1) {
        viewer.controls().disable();

        var event = function (e2) {
            var view = scene.view();
            var loc2  = view.screenToCoordinates({x : e2.clientX, y: e2.clientY});
            var position3 = { yaw: loc2.yaw, pitch: loc2.pitch};
            scene.hotspotContainer().createHotspot(imgTL, position3);
        };
        pano.addEventListener("mousemove", event, false);

        pano.addEventListener("mouseup", function mouseup (e3) {
                pano.removeEventListener("mousemove", event, false);
                var loc3  = view.screenToCoordinates({x : e3.clientX, y: e3.clientY});
                var position4 = { yaw: loc3.yaw, pitch: loc3.pitch};
                scene.hotspotContainer().createHotspot(imgTL, position4);
                pano.removeEventListener("mousedown", mousedown);
                pano.removeEventListener("mouseup", mouseup);
                viewer.controls().enable();
                tlListYaw[createTlFlag] = loc3.yaw;
                tlListPitch[createTlFlag] =loc3.pitch;
        })
    })
}

function createTS() {
    var imgTS = document.createElement('img');
    imgTS.src = trafficSigns.img;
    var position_contextmenu = { yaw: loc_contextmenu.yaw, pitch: loc_contextmenu.pitch};
    scene.hotspotContainer().createHotspot(imgTS, position_contextmenu);
    createTsFlag = createTsFlag + 1;
    tsListYaw[createTsFlag] = position_contextmenu.yaw;
    tsListPitch[createTsFlag] = position_contextmenu.pitch;   
    imgTS.addEventListener("mousedown", function mousedown (e1) {
        viewer.controls().disable();

        var event = function (e2) {
            var view = scene.view();
            var loc2  = view.screenToCoordinates({x : e2.clientX, y: e2.clientY});
            var position3 = { yaw: loc2.yaw, pitch: loc2.pitch};
            scene.hotspotContainer().createHotspot(imgTS, position3);
        };
        pano.addEventListener("mousemove", event, false);

         pano.addEventListener("mouseup", function mouseup (e3) {
                pano.removeEventListener("mousemove", event, false);
               
                var loc3  = view.screenToCoordinates({x : e3.clientX, y: e3.clientY});
                var position4 = { yaw: loc3.yaw, pitch: loc3.pitch};
                console.log(view.screenToCoordinates({x : e3.clientX, y: e3.clientY}));
                console.log(view.yaw + " - " + view.pitch);
                scene.hotspotContainer().createHotspot(imgTS, position4);
                pano.removeEventListener("mousedown", mousedown);
                pano.removeEventListener("mouseup", mouseup);
                viewer.controls().enable();
                tsListYaw[createTsFlag] = loc3.yaw;
                tsListPitch[createTsFlag] =loc3.pitch;
         })
    })
}

pano.addEventListener("contextmenu", function (event) {
    event.preventDefault();
    var contextElement = document.getElementById("context-menu");
    contextElement.style.top = event.offsetY + "px";
    contextElement.style.left = event.offsetX + "px";
    contextElement.classList.add("active");
    window.loc_contextmenu  = view.screenToCoordinates({x : event.clientX, y: event.clientY});
});

pano.addEventListener("click",function(){
  document.getElementById("context-menu").classList.remove("active");
});
