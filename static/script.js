$(document).ready(function () {
    var counter = 0;

    var switch_tun = function(tun_id) {
        console.log('click', tun_id);
        $.getJSON('/switch/?id=' + tun_id, function (data) {
            fill_table();
        })
    },  
    fill_table = function () {
        $.getJSON('/list', function (data) {
            $("#tuns_table > tbody > tr").remove();
            $.each(data, function (key, val) {
                var row = $("<tr>");
                var cols = '';
                cols += '<td>' + val['id'] + '</td>';
                if(val['enabled'] == true){
                    cols += '<td><a href="#' + val['id'] + '" class="tun_link badge badge-success">Yes</a></td>';
                }
                else{
                    cols += '<td><a href="#' + val['id'] + '" class="tun_link badge badge-secondary">No</a></td>';
                }
                
                if (val['status'] == true) {
                    cols += '<td><span class="badge badge-pill badge-success">On</span></td>';
                }
                else {
                    cols += '<td><span class="badge badge-pill badge-secondary">Off</span></td>';
                }
                cols += '<td>' + val['name'] + '</td>';
                cols += '<td><a href="' + val['url'] + '" target="tun' + val['id'] + '">' + val['url'] + '</a></td>';
                cols += '<td>' + val['note'] + '</td>';
                cols += '<td>' + val['cmd'] + '</td>';
                row.append(cols);
                $("#tuns_table > tbody").append(row);
            });
            $("a.tun_link").click(function (e) {
                switch_tun(e.target.hash.substring(1));
            });
        });
    };
    fill_table();
    setInterval(function () {
        fill_table();    
    }, 3000);
    
    
    
    
});