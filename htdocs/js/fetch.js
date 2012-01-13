function load_responses(data){
    data = jQuery.parseJSON(data)
    rv = ''
    for(var i = 0; i < data.responses.length; i++){
        rv += '<blockquote>' + data.responses[i].content + '</blockquote>';
    }
    jQuery('#response-container-' + data.id).html(rv)
}

function fetch_answer(id){
    jQuery.get(
        '/question/' + id, 
        function(data){
            load_responses(data);
        }
    );
}

function fetch_all_answers(){
    for(var i = 0; i < user.questions.length; i++){
        fetch_answer(user.questions[i]);
    }
}

jQuery(document).ready(function(){
     fetch_all_answers();
     setInterval("fetch_all_answers()", 5000);
});
