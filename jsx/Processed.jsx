// alert("Updated to version 6.1.0: Added functionality to group and rename VRayCryptomatte layers, enhancing organization and workflow efficiency.");
runMain();
function runMain() {
    try { app.currentTool = "moveTool"; } catch (error) { }
    // var file_path = "C:/bi_visual/data"
    var scriptFile = File($.fileName); // File hiện tại
    var parentFolder = scriptFile.parent.parent; // 📁 Lùi ra ngoài 1 cấp
    var file_path = parentFolder.fsName + "/data";
    // Kiểm tra xem đường dẫn thư mục có tồn tại không
    var folder = new Folder(file_path);
    if (folder.exists) {
        try {
            var processes = readFile(new File(file_path + "/processes.txt")).toString();
            if (processes == "0") {
                return;
            }
            var path_inputFolder = readFile(new File(file_path + "/inputFolder.txt")).toString();
            var name_PC = readFile(new File(file_path + "/computer_name.txt")).toString();
            var folderUser = name_PC;
            var inputFolder = path_inputFolder + "/processed/Temp/" + name_PC;
            var num_file_exr = getFilesInFolder(inputFolder);
            if (num_file_exr.length == 0) {
                return;
            }
            var mode = readFile(new File(file_path + "/mode.txt")).toString();
            main(inputFolder, mode, path_inputFolder, folderUser);
        } catch (error) {
            // alert("Err Main. " + error.message + " Line " + error.catch);
        }
    }

}
function main(inputFolder, mode, path_inputFolder, folderUser) {

    var History = []
    var done = 0;
    var unfinished = 0;

    var file_exr = getFilesInFolder(inputFolder);
    Progress("Working Processed");
    // Loop through Files array.
    var doc = app.activeDocument;
    var nameFile = doc.name.replace(/\.[^\.]+$/, '');
    try {
        //8, 16,32 mode 16-bit channel["8 Bits/Channel", "16 Bits/Channel", "32 Bits/Channel"]
        var mode_bit = 0;
        switch (true) {
            case mode == "8 Bits/Channel":
                mode_bit = 8;
                break;
            case mode == "16 Bits/Channel":
                mode_bit = 16;
                break;
            case mode == "32 Bits/Channel":
                mode_bit = 32;
                break;

            default:
                break;
        }
        // Progress.message("Change: " + mode);
        convertLayerTo16Bit(mode_bit);
        // Progress.message("Executing file : " + nameFile);
    } catch (error) {
        // alert("Only the 'mode x-bit channel' can be changed, replacing x with 8, 16, or 32.");
        unfinished++;
    }
    // xóa tất cả layer có tên VRay......none và đầu tên file VRayCryptomatte thành VRayCryptomatte.Mask_0001,VRayCryptomatte.Mask_0002
    // * @param { string } nameFilter - Tên cần lọc(ví dụ: "VRayCryptomatte"). 
    //  * Nếu null hoặc rỗng -> chỉ liệt kê layer, không đổi tên.
    //  * @param { string } renamePrefix - Tiền tố khi đổi tên(ví dụ: ".Mask_").
    //  * @param { number } paddingLength - Số chữ số padding(ví dụ: 4 -> "0001").
    var layerNamesArray = getAllLayerNames("VRayCryptomatte", ".Mask_", 4);
    for (var i = 0; i < layerNamesArray.length; i++) {
        var namelayer = layerNamesArray[i].toString();
        var parts = namelayer.split(".");
        var nameNewLayer = parts[parts.length - 1];
        if (namelayer.indexOf("VRay") == 0 && namelayer.lastIndexOf(".none") == namelayer.length - ".none".length) {
            selectLayerName(namelayer);
            deleteCurrentLayer();
            layerNamesArray.splice(i, 1);
        }
    }
    // layerNamesArray = getAllLayerNames();
    if (layerNamesArray.length > 0) {
        // Check if string starts with "VRay" and ends with "RGB"
        //Kiểm tra xem chuỗi có bắt đầu bằng "VRay" và kết thúc bằng "RGB" không
        var checkSelect1 = 0;
        for (var i = 0; i < layerNamesArray.length; i++) {
            var namelayer = layerNamesArray[i].toString();
            if (namelayer.indexOf("VRay") == 0 && namelayer.lastIndexOf(".RGB") == namelayer.length - ".RGB".length) {
                checkSelect1++;
                if (checkSelect1 === 1) {
                    selectLayerName(layerNamesArray[i]);
                }
                selectMultipleLayerName(layerNamesArray[i])
            }
        }
        if (checkSelect1 > 0) {
            newGroupMultipleLayer("Render Elements");
        }
        // check if the first 2 characters must be lowercase?
        // kiểm tra xem 2 ký tự đầu tiên có phải là chữ thường không?
        var checkSelect2 = 0;
        var dem = 0;
        for (var i = 0; i < layerNamesArray.length; i++) {
            var namelayer = layerNamesArray[i].toString().substring(0, 2);
            if (checkCase(namelayer) === true || isAlphaString(namelayer.toString()) === true) {
                checkSelect2++;
                if (checkSelect2 === 1) {
                    selectLayerName(layerNamesArray[i]);
                }
                selectMultipleLayerName(layerNamesArray[i])
                dem++;
            }
        }
        if (dem != 0) {
            newGroupMultipleLayer("Render Elements II");
        }
        if (checkSelect1 > 0) {
            selectMultipleLayerName("Render Elements");
        }
        moveLayerBottom();
        setColorGroup("Grn ");
        selectLayerName(layerNamesArray[0]);
        // MoveTo(checkSelect1 + checkSelect2 + 4);
        renameLayre("Rendering");
        setColorGroup("Rd  ");
        //tạo group  "VRayCryptomatte Mask"
        createGroup("VRayCryptomatte Mask");
        moveToBottom();

        var arrLayerName = [];
        for (var i = 0; i < layerNamesArray.length; i++) {
            var namelayer = layerNamesArray[i].toString();
            var parts = namelayer.split(".");
            var nameNewLayer = parts[parts.length - 1];
            if (namelayer.indexOf("VRay") == 0 && namelayer.lastIndexOf(".RGB") !== namelayer.length - ".RGB".length) {
                if (namelayer.indexOf(".<unknown>") === namelayer.length - ".<unknown>".length) {
                    var startIndex = "VRay".length;
                    var endIndex = namelayer.length - ".<unknown>".length;
                    var nameNewLayer = namelayer.substring(startIndex, endIndex);
                }
                if (namelayer.indexOf(".<unknown>") !== namelayer.length - ".<unknown>".length) {
                    arrLayerName.push(nameNewLayer);
                }
                seletLayerLoadSelection(namelayer);
                moveToGroup("VRayCryptomatte Mask");
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
        }
        //set color group
        selectLayerName("VRayCryptomatte Mask");
        setColorGroup("Vlt ");
        var nameGroup = getNameGroup();
        for (var i = 0; i < nameGroup.length; i++) {
            hdGroupName(nameGroup[i]);
        }
    } else {
        unfinished++;
    }
    //cập nhật thêm di chuyển layer qua Render Elements và xóa Render Elements II
    try {
        var renderElementsIIGroup = app.activeDocument.layerSets.getByName("Render Elements II");
        var renderElementsGroup = app.activeDocument.layerSets.getByName("Render Elements");
        if (renderElementsIIGroup && renderElementsGroup) {
            for (var i = renderElementsIIGroup.layers.length - 1; i >= 0; i--) {
                var layer = renderElementsIIGroup.layers[i];
                layer.move(renderElementsGroup, ElementPlacement.PLACEATBEGINNING);
            }
        }
        var renderElementsIIGroup = app.activeDocument.layerSets.getByName("Render Elements II");
        if (renderElementsIIGroup) {
            renderElementsIIGroup.remove();
        }
    } catch (error) { }

    // Lấy layer Rendering so sánh và xoá các layer giống layer Rendering
    try {
        selectLayerName("Rendering");
        var renderingLayer = app.activeDocument.layers.getByName("Rendering");
        var layersWithSameSelection = [];
        for (var i = 0; i < app.activeDocument.layers.length; i++) {
            var currentLayer = app.activeDocument.layers[i];
            if (currentLayer.bounds !== undefined && currentLayer.typename !== "LayerSet") {
                $.sleep(200);
                if (compareSelections(currentLayer, renderingLayer)) {

                    if (currentLayer !== renderingLayer) {
                        layersWithSameSelection.push(currentLayer);
                    }

                }
            }
        }
        if (layersWithSameSelection.length > 0) {
            for (var i = 0; i < layersWithSameSelection.length; i++) {
                layersWithSameSelection[i].remove();
                $.sleep(1000);
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
    var path_PSD = Folder(outputFolder + "/processed/Temp/" + folderUser);
    var path_png = Folder(outputFolder + "/processed");
    var path_png_prepost = Folder(outputFolder + "/prepost");
    if (!path_PSD.exists) {
        path_PSD.create();//create folder 
    }
    if (!path_png.exists) {
        path_png.create();//create folder 
    }
    if (!path_png_prepost.exists) {
        path_png_prepost.create();//create folder 
    }
    var doc = app.activeDocument;
    var nameFile = doc.name.replace(/\.[^\.]+$/, '');

    PSB(path_png, "");
    var filePath_processed = new File(path_png + "/" + nameFile + ".png");
    PNG(filePath_processed);
    // tránh ghi đè file PNG đã tồn tại trong folder prepost
    var filePath_prepost = new File(path_png_prepost + "/" + nameFile + ".png");
    if (!filePath_prepost.exists) {
        filePath_processed.copy(filePath_prepost);
    }

    done++;
    activeDocument.close(SaveOptions.DONOTSAVECHANGES);
}
// Function to check if a string contains only A-Z characters
function isAlphaString(inputString) {
    if (inputString.length === 1) {
        var regex = /^[A-Z]+$/;
        return regex.test(inputString);
    }
    else {
        return false;
    }
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
        // alert("Đã xảy ra lỗi khi ghi vào file: " + e);
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
    // // tránh ghi đè file PNG đã tồn tại
    // var filePath = new File(parentFolder + "/" + activeDocument.name.replace(/\.[^\.]+$/, '') + ".png");
    // if (!filePath.exists) {
    //     desc9.putPath(idIn, filePath);
    // } else {//để dừng hẳn hàm
    //     return;
    // }

    desc9.putPath(idIn, new File(parentFolder));
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
function getAllLayerNames(targetName, name, number) {
    var doc = app.activeDocument;
    var layerNames = [];
    var maskCounter = 1;

    function collectLayerNames(layerSet) {
        for (var i = 0; i < layerSet.layers.length; i++) {
            var currentLayer = layerSet.layers[i];

            if (currentLayer.typename === "ArtLayer") {

                // Nếu có targetName và trùng chính xác
                if (targetName && currentLayer.name === targetName) {
                    var newName = targetName + String(name) + zeroPad(maskCounter, Number(number));
                    currentLayer.name = newName;
                    maskCounter++;
                }

                layerNames.push(currentLayer.name);

            } else if (currentLayer.typename === "LayerSet") {
                collectLayerNames(currentLayer); // duyệt đệ quy
            }
        }
    }

    collectLayerNames(doc);

    return layerNames;
}

function zeroPad(num, places) {
    var zero = places - num.toString().length + 1;
    return Array(+(zero > 0 && zero)).join("0") + num;
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