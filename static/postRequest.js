/**
 * Created by tangh on 2017/10/8.
 */
function postJson(url,data) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function () {
        if(xhr.status == 280){
        var redirect_url = xhr.getResponseHeader("Location");
        location.href= redirect_url;
    }else if (xhr.readyState === 4 && xhr.status === 200) {

    }

    };


    var data = JSON.stringify(data);
    xhr.send(data);


}

function postJsonWithFunction(url,data,ednFunction) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function () {
        if(xhr.status == 280){
        var redirect_url = xhr.getResponseHeader("Location");
        location.href= redirect_url;
    }else if (xhr.readyState === 4 && xhr.status === 200) {

            ednFunction();
    }

    };


    var data = JSON.stringify(data);
    xhr.send(data);


}
function postJsonWithFunctionParaIsResponseContent(url,data,ednFunction) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function () {
        if(xhr.status == 280){
        var redirect_url = xhr.getResponseHeader("Location");
        location.href= redirect_url;
    }else if (xhr.readyState === 4 && xhr.status === 200) {

            ednFunction(xhr.responseText);
    }

    };


    var data = JSON.stringify(data);
    xhr.send(data);


}
