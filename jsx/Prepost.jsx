// alert("Updated to version 6.1.0: Improved prepost processing with enhanced layer management and color coding for better organization.");
runMain();
function runMain() {
    Progress("Working Prepost");
    // var file_path = "C:/bi_visual/data"
    // var scriptFile = File($.fileName); // Lấy đối tượng File của script đang chạy
    // var file_path = scriptFile.parent.fsName.toString() + "/data";
    var scriptFile = File($.fileName); // File hiện tại
    var parentFolder = scriptFile.parent.parent; // 📁 Lùi ra ngoài 1 cấp
    var file_path = parentFolder.fsName + "/data";
    // Kiểm tra xem đường dẫn thư mục có tồn tại không
    var folder = new Folder(file_path);
    if (folder.exists) {
        try {
            var prepost = readFile(new File(file_path + "/preposr.txt")).toString();
            if (prepost == "0") {
                return;
            }
            var path_pngFile = readFileTxt(file_path.toString() + "/pngFile.txt");
            var path_inputFolder = readFile(new File(file_path + "/inputFolder.txt")).toString();
            var path_Folder_Processed = Folder(path_inputFolder + "/processed");//prepost

            for (var i = 0; i < path_pngFile.length; i++) {
                var pathFile = new File(path_pngFile[i]);
                var pngFileName = pathFile.displayName.toString();
                var psdFileName = pngFileName.replace(/\.png$/, ".psb");
                // open file psb
                var checkOpenFile = openPSDFile(path_Folder_Processed, psdFileName);
                if (checkOpenFile == true) {
                    selectLayerName("Rendering");
                    removeLayer();
                    placeImgFrame(pathFile.toString(), 100)
                    renameLayre("Rendering");
                    rasterize_Layer();
                    setColorGroup("Rd  ");
                    var getColorOrange = getAllLayersWithColor("orange");
                    var getColorYellow = getAllLayersWithColor("yellowColor");
                    for (var a = 0; a < getColorOrange.length; a++) {
                        getColorOrange[a].remove();
                    }
                    for (var a = 0; a < getColorYellow.length; a++) {
                        getColorYellow[a].remove();
                    }
                    // violet
                    var doc = app.activeDocument;
                    var CodeColorToFind = "violet"; // Màu cần tìm
                    var arrLayerName = [];
                    var layerNamesWithColorViolet = getAllLayerNamesWithColorInDocument(doc, CodeColorToFind).reverse();
                    for (var a = 0; a < layerNamesWithColorViolet.length; a++) {

                        var namelayer = layerNamesWithColorViolet[a].toString();
                        var parts = namelayer.split(".");
                        var nameNewLayer = parts[parts.length - 1];

                        if (namelayer.indexOf(".<unknown>") === namelayer.length - ".<unknown>".length) {
                            var startIndex = "VRay".length;
                            var endIndex = namelayer.length - ".<unknown>".length;
                            var nameNewLayer = namelayer.substring(startIndex, endIndex);
                        }
                        if (namelayer.indexOf(".<unknown>") !== namelayer.length - ".<unknown>".length) {
                            arrLayerName.push(nameNewLayer);
                        }
                        seletLayerLoadSelection(namelayer);
                        selectLayerName("Rendering");
                        dupLayerToSelection();
                        renameLayre(nameNewLayer);
                        if (namelayer.indexOf(".<unknown>") === namelayer.length - ".<unknown>".length) {
                            setColorGroup("Ylw ");
                        }
                        else {
                            setColorGroup("Orng");
                        }

                    }
                    var getColorOrange = getAllLayersWithColor("orange");
                    for (var x = 0; x < getColorOrange.length; x++) {
                        if (x == 0) {
                            selectLayerName(getColorOrange[x].name.toString());
                        }
                        else {
                            selectMultipleLayerName(getColorOrange[x].name.toString());
                        }
                    }
                    var getColorYellow = getAllLayersWithColor("yellowColor");
                    for (var x = 0; x < getColorYellow.length; x++) {
                        selectMultipleLayerName(getColorYellow[x].name.toString());
                    }
                    newGroupMultipleLayer("Render Elements");
                    setColorGroup("Orng");
                    // Lấy tất cả các layer trong tài liệu
                    var layers = app.activeDocument.layers;
                    // Biến để lưu trữ số lượng layer và số lượng nhóm
                    var totalCounts = { layerCount: 0, groupCount: 0 };
                    // Duyệt qua từng layer và tính tổng số lượng layer và nhóm bằng cách gọi hàm đệ quy
                    for (var i = 0; i < layers.length; i++) {
                        var counts = countLayersAndGroups(layers[i]);
                        totalCounts.layerCount += counts.layerCount;
                        totalCounts.groupCount += counts.groupCount;
                    }
                    MoveTo(totalCounts.layerCount + (totalCounts.groupCount * 2));
                    //xóa group VRayCryptomatte Mask
                    selectLayerName("VRayCryptomatte Mask");
                    var docRef = app.activeDocument;
                    var activeLayer = docRef.activeLayer;
                    activeLayer.remove();

                    //xóa layer giống layer Rendering
                    try {
                        selectLayerName("Rendering");
                        var renderingLayer = app.activeDocument.layers.getByName("Rendering");
                        var layersWithSameSelection = [];

                        function removeLayersWithSameSelection(layer) {
                            if (layer.bounds !== undefined && layer.typename !== "LayerSet") {
                                if (compareSelections(layer, renderingLayer)) {
                                    if (layer !== renderingLayer) {
                                        layersWithSameSelection.push(layer);
                                    }
                                }
                            } else if (layer.typename === "LayerSet") {
                                for (var i = 0; i < layer.layers.length; i++) {
                                    removeLayersWithSameSelection(layer.layers[i]);
                                }
                            }
                        }

                        for (var i = 0; i < app.activeDocument.layers.length; i++) {
                            removeLayersWithSameSelection(app.activeDocument.layers[i]);
                        }

                        if (layersWithSameSelection.length > 0) {
                            for (var i = 0; i < layersWithSameSelection.length; i++) {
                                layersWithSameSelection[i].remove();
                            }
                        }

                        function compareSelections(layer1, layer2) {
                            var bounds1 = layer1.bounds;
                            var bounds2 = layer2.bounds;
                            for (var k = 0; k < 4; k++) {
                                if (bounds1[k].value !== bounds2[k].value) {
                                    return false;
                                }
                            }
                            return true;
                        }
                    } catch (error) { }

                    var outputFolder = Folder(path_inputFolder);
                    var processed = Folder(outputFolder + "/prepost");
                    if (!processed.exists) {
                        processed.create();//create folder 
                    }
                    PSB(processed, "");
                    app.activeDocument.close(SaveOptions.DONOTSAVECHANGES);
                }

                else {
                    continue;
                }
            }
        } catch (error) {
            // alert("Err Main. " + error.message + " Line " + error.catch);
        }

    }

}
function countLayersAndGroups(layer) {
    var layerCount = 0;
    var groupCount = 0;

    // Kiểm tra xem layer có phải là một nhóm không
    if (layer.typename === "LayerSet") {
        // Nếu là nhóm, tăng biến đếm số lượng nhóm
        groupCount++;

        // Duyệt qua tất cả các layer trong nhóm và gọi đệ quy
        for (var i = 0; i < layer.layers.length; i++) {
            var counts = countLayersAndGroups(layer.layers[i]);
            layerCount += counts.layerCount;
            groupCount += counts.groupCount;
        }
    } else {
        // Nếu không phải là nhóm, tăng biến đếm số lượng layer
        layerCount++;
    }

    return { layerCount: layerCount, groupCount: groupCount };
}
function getAllLayerNamesWithColorInDocument(doc, CodeColor) {
    var layers = doc.layers;
    var layerNamesWithColor = [];

    for (var a = 0; a < layers.length; a++) {
        var currentLayer = layers[a];

        if (currentLayer.typename === "ArtLayer") {
            var ref = new ActionReference();
            ref.putIdentifier(charIDToTypeID("Lyr "), currentLayer.id);
            var desc = executeActionGet(ref);

            if (desc.hasKey(stringIDToTypeID("color"))) {
                var colorID = desc.getEnumerationValue(stringIDToTypeID("color"));
                var colorName = typeIDToStringID(colorID);

                if (colorName === CodeColor) {
                    layerNamesWithColor.push(currentLayer.name);
                }
            }
        } else if (currentLayer.typename === "LayerSet") { // Nếu là một nhóm
            // Gọi đệ quy để tìm trong nhóm
            var layerNamesInGroup = getAllLayerNamesWithColorInDocument(currentLayer, CodeColor);
            layerNamesWithColor = layerNamesWithColor.concat(layerNamesInGroup);
        }
    }

    return layerNamesWithColor;
}
function getAllLayersWithColor(CodeColor) {
    var doc = app.activeDocument;
    var layers = doc.layers;
    var layersName = [];
    for (var a = 0; a < layers.length; a++) {
        var layer = layers[a];
        var isVisible = layer.visible;
        if (layer.typename === "ArtLayer") {
            var ref = new ActionReference();
            ref.putIdentifier(charIDToTypeID("Lyr "), layer.id);
            var desc = executeActionGet(ref);
            if (desc.hasKey(stringIDToTypeID("color"))) {
                var colorID = desc.getEnumerationValue(stringIDToTypeID("color"));
                var colorName = typeIDToStringID(colorID);
                if (colorName === CodeColor) {
                    layersName.push(layer);
                }
            }
        }
    }
    return layersName;
}

function rasterize_Layer() {
    // =======================================================
    var idrasterizeLayer = stringIDToTypeID("rasterizeLayer");
    var desc428 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref47 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    var idOrdn = charIDToTypeID("Ordn");
    var idTrgt = charIDToTypeID("Trgt");
    ref47.putEnumerated(idLyr, idOrdn, idTrgt);
    desc428.putReference(idnull, ref47);
    executeAction(idrasterizeLayer, desc428, DialogModes.NO);
}
// delete layer
function removeLayer() {
    // =======================================================
    var idDlt = charIDToTypeID("Dlt ");
    var desc421 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref44 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    var idOrdn = charIDToTypeID("Ordn");
    var idTrgt = charIDToTypeID("Trgt");
    ref44.putEnumerated(idLyr, idOrdn, idTrgt);
    desc421.putReference(idnull, ref44);
    var idLyrI = charIDToTypeID("LyrI");
    var list30 = new ActionList();
    list30.putInteger(34);
    desc421.putList(idLyrI, list30);
    executeAction(idDlt, desc421, DialogModes.NO);

}
function placeImgFrame(imgPath, num) {
    var idplaceEvent = stringIDToTypeID("placeEvent");
    var desc291 = new ActionDescriptor();
    var idID = stringIDToTypeID("ID");
    desc291.putInteger(idID, 365);
    var idnull = stringIDToTypeID("null");
    desc291.putPath(idnull, new File(imgPath));
    var idlinked = stringIDToTypeID("linked");
    desc291.putBoolean(idlinked, true);
    var idfreeTransformCenterState = stringIDToTypeID("freeTransformCenterState");
    var idquadCenterState = stringIDToTypeID("quadCenterState");
    var idQCSAverage = stringIDToTypeID("QCSAverage");
    desc291.putEnumerated(idfreeTransformCenterState, idquadCenterState, idQCSAverage);
    desc291.putUnitDouble(stringIDToTypeID("width"), stringIDToTypeID("percentUnit"), num);
    desc291.putUnitDouble(stringIDToTypeID("height"), stringIDToTypeID("percentUnit"), num);
    // executeAction(stringIDToTypeID("transform"),desc291,DialogModes.NO);
    var idoffset = stringIDToTypeID("offset");
    var desc292 = new ActionDescriptor();
    var idhorizontal = stringIDToTypeID("horizontal");
    var idpixelsUnit = stringIDToTypeID("pixelsUnit");
    desc292.putUnitDouble(idhorizontal, idpixelsUnit, 0.000000);
    var idvertical = stringIDToTypeID("vertical");
    var idpixelsUnit = stringIDToTypeID("pixelsUnit");
    desc292.putUnitDouble(idvertical, idpixelsUnit, 0.000000);
    var idoffset = stringIDToTypeID("offset");
    desc291.putObject(idoffset, idoffset, desc292);
    var idreplaceLayer = stringIDToTypeID("replaceLayer");
    var desc293 = new ActionDescriptor();
    var idfrom = stringIDToTypeID("from");
    var ref9 = new ActionReference();
    var idlayer = stringIDToTypeID("layer");
    ref9.putIdentifier(idlayer, 359);
    desc293.putReference(idfrom, ref9);
    var idto = stringIDToTypeID("to");
    var ref10 = new ActionReference();
    var idlayer = stringIDToTypeID("layer");
    ref10.putIdentifier(idlayer, 365);
    desc293.putReference(idto, ref10);
    var idplaceEvent = stringIDToTypeID("placeEvent");
    desc291.putObject(idreplaceLayer, idplaceEvent, desc293);
    executeAction(idplaceEvent, desc291, DialogModes.NO);
}
// Định nghĩa hàm để mở tệp PSD dựa trên đường dẫn và tên tệp
function openPSDFile(folderPath, fileName) {
    var folder = new Folder(folderPath);

    if (folder.exists) {
        var files = folder.getFiles(function (file) {
            // alert(file.displayName.toString().replace(/%20/g, " ") + "         00 " + fileName)
            return (file instanceof File) && file.displayName.toString().replace(/%20/g, " ") === fileName;
        });

        if (files.length > 0) {
            var psdFile = files[0];

            if (psdFile.exists) {
                app.open(psdFile);
                return true;
            } else {
                // alert("Tệp PSD không tồn tại.");
                return false;
            }
        } else {
            // alert("Không tìm thấy tệp PSD có tên " + fileName + " trong thư mục.");
            return false;
        }
    } else {
        // alert("Thư mục không tồn tại.");
        return false;
    }
}
// function openPSDFile(folderPath, fileName) {
//     var folder = new Folder(folderPath);

//     if (folder.exists) {
//         var files = folder.getFiles(function (file) {
//             return (file instanceof File) && file.name.toString().replace(/%20/g, " ") === fileName;
//         });
//         if (files.length > 0) {
//             var psdFile = files[0];

//             if (psdFile.exists) {
//                 app.open(psdFile);
//                 return true;
//             } else {
//                 return false;
//             }
//         } else {
//             var subfolders = folder.getFiles(function (file) {
//                 return (file instanceof Folder);
//             });

//             for (var i = 0; i < subfolders.length; i++) {
//                 var subfolder = subfolders[i];
//                 if (openPSDFile(subfolder.fsName, fileName)) {
//                     return true;
//                 }
//             }
//             return false;
//         }
//     } else {
//         return false;
//     }
// }

function readFileTxt(filePath) {
    // var filePath = "Đường_dẫn_đến_tệp_văn_bản.txt"; // Thay thế bằng đường dẫn đến tệp văn bản thực tế
    var file = new File(filePath);
    if (file.exists) {
        file.open("r"); // Mở tệp để đọc
        var lines = [];
        while (!file.eof) {
            var line = file.readln();
            lines.push(line);
        }
        file.close(); // Đóng tệp sau khi đọc xong
        // for (var i = 0; i < lines.length; i++) {
        //     alert(lines[i]);
        // }
    } else {
        alert("File does not exist.");
    }
    return lines;
}

function writeFile(newFile, fileContent) {
    newFile.encoding = "UTF-8";
    newFile.open("w");
    newFile.write(fileContent);
    newFile.close();
}
function readFile(file) {
    var contentArray = [];
    if (file.exists) {
        file.open("r");
        var content = file.read();
        file.close();

        if (content) {
            contentArray = content.split(",");
        }
    }
    return contentArray;
}
function hdGroupName(nameGroup) {
    // =======================================================
    var idHd = charIDToTypeID("Hd  ");
    var desc264 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var list19 = new ActionList();
    var ref23 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    ref23.putName(idLyr, nameGroup);
    list19.putReference(ref23);
    desc264.putList(idnull, list19);
    executeAction(idHd, desc264, DialogModes.NO);
}
//lấy danh sách tên group
function getNameGroup() {
    var doc = app.activeDocument;
    var numberOfItems = doc.layers.length;
    var groupNames = [];

    for (var i = 0; i < numberOfItems; i++) {
        var currentItem = doc.layers[i];

        if (currentItem.typename === "LayerSet") {
            groupNames.push(currentItem.name);
        }
    }
    return groupNames;
}
//ghi lịch sử
function appendToTextFile(filePath, content) {
    var file = new File(filePath);
    try {
        file.open("a");
        file.writeln(content);
    } catch (e) {
        alert("An error occurred while writing to the file: " + e);
    } finally {
        file.close();
    }
}
// Di chuyển layer xuống dưới cùng
function moveToBottom() {
    var doc = app.activeDocument;
    var targetLayerIndex = doc.layers.length - 1; // Chỉ số của layer cuối cùng
    var layerToMove = doc.activeLayer;
    layerToMove.move(doc.layers[targetLayerIndex], ElementPlacement.PLACEAFTER);
}

// Di chuyển layer đang chọn vào nhóm
function moveToGroup(targetGroupName) {
    var doc = app.activeDocument;
    var targetGroup = doc.layerSets.getByName(targetGroupName);
    var selectedLayer = doc.activeLayer;
    selectedLayer.move(targetGroup, ElementPlacement.INSIDE);
}
// lấy thông tin phần tử trong mảng
function customIndexOf(array, element) {
    for (var i = 0; i < array.length; i++) {
        if (array[i] === element) {
            return i;
        }
    }
    return -1;
}
function deleteCurrentLayer() {
    var idDlt = charIDToTypeID("Dlt ");
    var desc232 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref5 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    var idOrdn = charIDToTypeID("Ordn");
    var idTrgt = charIDToTypeID("Trgt");
    ref5.putEnumerated(idLyr, idOrdn, idTrgt);
    desc232.putReference(idnull, ref5);
    var idLyrI = charIDToTypeID("LyrI");
    var list7 = new ActionList();
    list7.putInteger(20);
    desc232.putList(idLyrI, list7);
    executeAction(idDlt, desc232, DialogModes.NO);
}
function createGroup(groupNAme) {
    // =======================================================
    var idMk = charIDToTypeID("Mk  ");
    var desc259 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref16 = new ActionReference();
    var idlayerSection = stringIDToTypeID("layerSection");
    ref16.putClass(idlayerSection);
    desc259.putReference(idnull, ref16);
    var idlayerSectionStart = stringIDToTypeID("layerSectionStart");
    desc259.putInteger(idlayerSectionStart, 39);
    var idlayerSectionEnd = stringIDToTypeID("layerSectionEnd");
    desc259.putInteger(idlayerSectionEnd, 40);
    var idNm = charIDToTypeID("Nm  ");
    desc259.putString(idNm, "Group 1");
    executeAction(idMk, desc259, DialogModes.NO);
    // =======================================================
    var idsetd = charIDToTypeID("setd");
    var desc261 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref17 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    var idOrdn = charIDToTypeID("Ordn");
    var idTrgt = charIDToTypeID("Trgt");
    ref17.putEnumerated(idLyr, idOrdn, idTrgt);
    desc261.putReference(idnull, ref17);
    var idT = charIDToTypeID("T   ");
    var desc262 = new ActionDescriptor();
    var idNm = charIDToTypeID("Nm  ");
    desc262.putString(idNm, groupNAme);
    var idLyr = charIDToTypeID("Lyr ");
    desc261.putObject(idT, idLyr, desc262);
    executeAction(idsetd, desc261, DialogModes.NO);
}
function PNG(parentFolder) {
    var idsave = charIDToTypeID("save");
    var desc9 = new ActionDescriptor();
    var idAs = charIDToTypeID("As  ");
    var desc10 = new ActionDescriptor();
    var idMthd = charIDToTypeID("Mthd");
    var idPNGMethod = stringIDToTypeID("PNGMethod");
    var idquick = stringIDToTypeID("quick");
    desc10.putEnumerated(idMthd, idPNGMethod, idquick);
    var idPGIT = charIDToTypeID("PGIT");
    var idPGIT = charIDToTypeID("PGIT");
    var idPGIN = charIDToTypeID("PGIN");
    desc10.putEnumerated(idPGIT, idPGIT, idPGIN);
    var idPNGf = charIDToTypeID("PNGf");
    var idPNGf = charIDToTypeID("PNGf");
    var idPGAd = charIDToTypeID("PGAd");
    desc10.putEnumerated(idPNGf, idPNGf, idPGAd);
    var idCmpr = charIDToTypeID("Cmpr");
    desc10.putInteger(idCmpr, 6);
    var idPNGF = charIDToTypeID("PNGF");
    desc9.putObject(idAs, idPNGF, desc10);
    var idIn = charIDToTypeID("In  ");
    desc9.putPath(idIn, new File(parentFolder + "/" + activeDocument.name.replace(/\.[^\.]+$/, '') + ".png"));
    var idDocI = charIDToTypeID("DocI");
    desc9.putInteger(idDocI, 1164);
    var idCpy = charIDToTypeID("Cpy ");
    desc9.putBoolean(idCpy, true);
    var idsaveStage = stringIDToTypeID("saveStage");
    var idsaveStageType = stringIDToTypeID("saveStageType");
    var idsaveSucceeded = stringIDToTypeID("saveSucceeded");
    desc9.putEnumerated(idsaveStage, idsaveStageType, idsaveSucceeded);
    executeAction(idsave, desc9, DialogModes.NO);
}
function PSB(parentFolder, processed) {
    // savePSB(app.activeDocument.path);
    var doc = app.activeDocument;
    var str = String(doc.name.replace(/\.[^\.]+$/, ''));
    // var nameDoc = str.split(".")[0];
    var saveFile = parentFolder + "/" + str + processed + ".psb";
    var desc1 = new ActionDescriptor();
    var desc2 = new ActionDescriptor();
    desc2.putBoolean(stringIDToTypeID('maximizeCompatibility'), true);
    desc1.putObject(charIDToTypeID('As  '), charIDToTypeID('Pht8'), desc2);
    desc1.putPath(charIDToTypeID('In  '), new File(saveFile));
    desc1.putBoolean(charIDToTypeID('LwCs'), true);
    executeAction(charIDToTypeID('save'), desc1, DialogModes.NO);
    // activeDocument.close(SaveOptions.DONOTSAVECHANGES);
}
function getFilesInFolder(folder) {
    var folder1 = Folder(String(folder));
    var files = [];
    var items = folder1.getFiles();
    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        if (item instanceof File && item.name.match(/\.exr$/i)) {
            files.push(item);
        }
    }
    return files;
}

function convertLayerTo16Bit(num) {
    var idCnvM = charIDToTypeID("CnvM");
    var desc232 = new ActionDescriptor();
    var idDpth = charIDToTypeID("Dpth");
    desc232.putInteger(idDpth, num);
    var idMrge = charIDToTypeID("Mrge");
    desc232.putBoolean(idMrge, false);
    executeAction(idCnvM, desc232, DialogModes.NO);
}
function dupLayerToSelection() {
    var idCpTL = charIDToTypeID("CpTL");
    executeAction(idCpTL, undefined, DialogModes.NO);
}
function deleteCurrentLayer() {
    var idDlt = charIDToTypeID("Dlt ");
    var desc409 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref135 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    var idOrdn = charIDToTypeID("Ordn");
    var idTrgt = charIDToTypeID("Trgt");
    ref135.putEnumerated(idLyr, idOrdn, idTrgt);
    desc409.putReference(idnull, ref135);
    var idLyrI = charIDToTypeID("LyrI");
    var list113 = new ActionList();
    list113.putInteger(24);
    desc409.putList(idLyrI, list113);
    executeAction(idDlt, desc409, DialogModes.NO);
}
function seletLayerLoadSelection(layerName) {
    var idslct = charIDToTypeID("slct");
    var desc389 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref125 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    ref125.putName(idLyr, layerName);
    desc389.putReference(idnull, ref125);
    var idMkVs = charIDToTypeID("MkVs");
    desc389.putBoolean(idMkVs, false);
    var idLyrI = charIDToTypeID("LyrI");
    var list108 = new ActionList();
    list108.putInteger(9);
    desc389.putList(idLyrI, list108);
    executeAction(idslct, desc389, DialogModes.NO);

    var idsetd = charIDToTypeID("setd");
    var desc391 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref126 = new ActionReference();
    var idChnl = charIDToTypeID("Chnl");
    var idfsel = charIDToTypeID("fsel");
    ref126.putProperty(idChnl, idfsel);
    desc391.putReference(idnull, ref126);
    var idT = charIDToTypeID("T   ");
    var ref127 = new ActionReference();
    var idChnl = charIDToTypeID("Chnl");
    var idChnl = charIDToTypeID("Chnl");
    var idTrsp = charIDToTypeID("Trsp");
    ref127.putEnumerated(idChnl, idChnl, idTrsp);
    desc391.putReference(idT, ref127);
    executeAction(idsetd, desc391, DialogModes.NO);

}
function renameLayre(layerName) {
    var doc = app.activeDocument;
    var activeLayer = doc.activeLayer;
    activeLayer.name = layerName;
}
function MoveTo(num) {
    var idmove = charIDToTypeID("move");
    var desc99 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref26 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    var idOrdn = charIDToTypeID("Ordn");
    var idTrgt = charIDToTypeID("Trgt");
    ref26.putEnumerated(idLyr, idOrdn, idTrgt);
    desc99.putReference(idnull, ref26);
    var idT = charIDToTypeID("T   ");
    var ref27 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    ref27.putIndex(idLyr, num);
    desc99.putReference(idT, ref27);
    var idAdjs = charIDToTypeID("Adjs");
    desc99.putBoolean(idAdjs, false);
    var idVrsn = charIDToTypeID("Vrsn");
    desc99.putInteger(idVrsn, 5);
    var idLyrI = charIDToTypeID("LyrI");
    var list7 = new ActionList();
    list7.putInteger(19);
    desc99.putList(idLyrI, list7);
    executeAction(idmove, desc99, DialogModes.NO);
}
function setColorGroup(color_code) {
    var idsetd = charIDToTypeID("setd");
    var desc236 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref4 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    var idOrdn = charIDToTypeID("Ordn");
    var idTrgt = charIDToTypeID("Trgt");
    ref4.putEnumerated(idLyr, idOrdn, idTrgt);
    desc236.putReference(idnull, ref4);
    var idT = charIDToTypeID("T   ");
    var desc237 = new ActionDescriptor();
    var idClr = charIDToTypeID("Clr ");
    var idClr = charIDToTypeID("Clr ");
    var idYlw = charIDToTypeID(color_code);
    desc237.putEnumerated(idClr, idClr, idYlw);
    var idLyr = charIDToTypeID("Lyr ");
    desc236.putObject(idT, idLyr, desc237);
    executeAction(idsetd, desc236, DialogModes.NO);
}
function moveLayerBottom() {
    var idmove = charIDToTypeID("move");
    var desc338 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref73 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    var idOrdn = charIDToTypeID("Ordn");
    var idTrgt = charIDToTypeID("Trgt");
    ref73.putEnumerated(idLyr, idOrdn, idTrgt);
    desc338.putReference(idnull, ref73);
    var idT = charIDToTypeID("T   ");
    var ref74 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    ref74.putIndex(idLyr, 0);
    desc338.putReference(idT, ref74);
    var idAdjs = charIDToTypeID("Adjs");
    desc338.putBoolean(idAdjs, false);
    var idVrsn = charIDToTypeID("Vrsn");
    desc338.putInteger(idVrsn, 5);
    var idLyrI = charIDToTypeID("LyrI");
    var list34 = new ActionList();
    desc338.putList(idLyrI, list34);
    executeAction(idmove, desc338, DialogModes.NO);
}
function checkCase(str) {
    if (str === str.toLowerCase()) {
        return true;
    } else if (str === str.toUpperCase()) {
        return false;
    } else {
        return null;
    }
}
function selectLayerName(layerName) {
    try {
        var idslct = charIDToTypeID("slct");
        var desc305 = new ActionDescriptor();
        var idnull = charIDToTypeID("null");
        var ref56 = new ActionReference();
        var idLyr = charIDToTypeID("Lyr ");
        ref56.putName(idLyr, layerName);
        desc305.putReference(idnull, ref56);
        var idMkVs = charIDToTypeID("MkVs");
        desc305.putBoolean(idMkVs, false);
        var idLyrI = charIDToTypeID("LyrI");
        var list27 = new ActionList();
        list27.putInteger(19);
        desc305.putList(idLyrI, list27);
        executeAction(idslct, desc305, DialogModes.NO);

    } catch (error) {

    }
}
function selectMultipleLayerName(layername) {
    var idslct = charIDToTypeID("slct");
    var desc229 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref7 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    ref7.putName(idLyr, layername);
    desc229.putReference(idnull, ref7);
    var idselectionModifier = stringIDToTypeID("selectionModifier");
    var idselectionModifierType = stringIDToTypeID("selectionModifierType");
    var idaddToSelection = stringIDToTypeID("addToSelection");
    desc229.putEnumerated(idselectionModifier, idselectionModifierType, idaddToSelection);
    var idMkVs = charIDToTypeID("MkVs");
    desc229.putBoolean(idMkVs, false);
    var idLyrI = charIDToTypeID("LyrI");
    var list8 = new ActionList();
    list8.putInteger(22);
    list8.putInteger(23);
    desc229.putList(idLyrI, list8);
    executeAction(idslct, desc229, DialogModes.NO);
}
function getAllLayerNames() {
    var doc = app.activeDocument;
    var layers = doc.layers;
    var layerNames = [];

    function collectLayerNames(layerSet) {
        for (var i = 0; i < layerSet.layers.length; i++) {
            var currentLayer = layerSet.layers[i];
            if (currentLayer.typename === "ArtLayer") {
                layerNames.push(currentLayer.name);
                // } else if (currentLayer.typename === "LayerSet") {
                //     collectLayerNames(currentLayer);
            }
        }
    }

    collectLayerNames(doc);

    return layerNames;
}

function newGroupMultipleLayer(groupName) {
    var idMk = charIDToTypeID("Mk  ");
    var desc235 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref11 = new ActionReference();
    var idlayerSection = stringIDToTypeID("layerSection");
    ref11.putClass(idlayerSection);
    desc235.putReference(idnull, ref11);
    var idFrom = charIDToTypeID("From");
    var ref12 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    var idOrdn = charIDToTypeID("Ordn");
    var idTrgt = charIDToTypeID("Trgt");
    ref12.putEnumerated(idLyr, idOrdn, idTrgt);
    desc235.putReference(idFrom, ref12);
    var idlayerSectionStart = stringIDToTypeID("layerSectionStart");
    desc235.putInteger(idlayerSectionStart, 26);
    var idlayerSectionEnd = stringIDToTypeID("layerSectionEnd");
    desc235.putInteger(idlayerSectionEnd, 27);
    var idNm = charIDToTypeID("Nm  ");
    desc235.putString(idNm, "Group 1");
    executeAction(idMk, desc235, DialogModes.NO);

    var idsetd = charIDToTypeID("setd");
    var desc237 = new ActionDescriptor();
    var idnull = charIDToTypeID("null");
    var ref13 = new ActionReference();
    var idLyr = charIDToTypeID("Lyr ");
    var idOrdn = charIDToTypeID("Ordn");
    var idTrgt = charIDToTypeID("Trgt");
    ref13.putEnumerated(idLyr, idOrdn, idTrgt);
    desc237.putReference(idnull, ref13);
    var idT = charIDToTypeID("T   ");
    var desc238 = new ActionDescriptor();
    var idNm = charIDToTypeID("Nm  ");
    desc238.putString(idNm, groupName);
    var idLyr = charIDToTypeID("Lyr ");
    desc237.putObject(idT, idLyr, desc238);
    executeAction(idsetd, desc237, DialogModes.NO);
}
function Progress(message) {
    var b;
    var t;
    var w;
    var h;
    var g;

    w = new Window("palette", "Progress");
    g = w.add("group");
    b = g.add("progressbar");
    b.preferredSize = [410, -1];
    h = g.add("statictext", undefined, "0%");
    h.preferredSize = [40, -1];
    t = w.add("statictext", undefined, message);
    t.justify = "center";
    t.preferredSize = [450, -1];

    Progress.close = function () {
        w.close();
    };

    Progress.increment = function () {
        b.value++;
        var percent = Math.floor((b.value / b.maxvalue) * 100);
        h.text = percent + "%";
        app.refresh();
    };

    Progress.message = function (newMessage) {
        t.text = newMessage;
        app.refresh();
    };

    Progress.set = function (steps) {
        b.value = 0;
        b.minvalue = 0;
        b.maxvalue = steps;
    };

    w.show();
    app.refresh();
}