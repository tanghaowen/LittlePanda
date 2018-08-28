



function getJsonWithFunctionParaIsResponseContent(url,ednFunction) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);

    xhr.onreadystatechange = function () {
        if(xhr.status == 280){
        var redirect_url = xhr.getResponseHeader("Location");
        location.href= redirect_url;
    }else if (xhr.readyState === 4 && xhr.status === 200) {

            ednFunction(xhr.responseText);
    }

    };


    xhr.send(null);


}

