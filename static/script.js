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
                cols += '<td class="align-middle">' + val['id'] + '</td>';
                if(val['enabled'] == true){
                    cols += '<td class="align-middle"><small><a href="#' + val['id'] + '" class="tun_link text-success"><img id="x' + val['id'] + '" src="toggle-on.svg" alt="" width="32" height="32" title="On"></a></small></td>';
                }
                else{
                    cols += '<td class="align-middle"><a  href="#' + val['id'] + '" class="tun_link"><img id="x' + val['id'] + '" src="toggle-off.svg" alt="" width="32" height="32" title="Off"></a></td>';
                }
                
                if (val['status'] == true) {
                    cols += '<td class="align-middle"><img src="circle-fill.svg" alt="" width="24" height="24" title="On"></td>';
                }
                else {
                    cols += '<td class="align-middle"><img src="circle.svg" alt="" width="24" height="24" title="Off"></td>';
                }
                cols += '<td class="align-middle"><nobr><small>' + val['name'] + '</small></nobr></td>';
                if (val['url'].startsWith('htt')){
                    cols += '<td class="align-middle"><small><a href="' + val['url'] + '" target="tun' + val['id'] + '">' + val['url'] + '</a> ' + val['note'] + '</small></td>';
                } else{
                    cols += '<td class="align-middle"><small>' + val['url'] + val['note'] + '</small></td>';
                }
                cols += '<td class="align-middle"><small>' + val['cmd'] + '</small></td>';
                row.append(cols);
                $("#tuns_table > tbody").append(row);
            });
            $("a.tun_link").click(function(e) {
                console.log(e);
                switch_tun(e.target.id.substring(1));
            });
        });
    };
    fill_table();
    setInterval(function () {
        fill_table();    
    }, 3000);
});