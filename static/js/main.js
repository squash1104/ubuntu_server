$(document).ready(function(){
    // Aplica a máscara a todos os inputs com name="telefone" e name="contato"
    // que são os campos que usamos para telefones/contato
    $('input[name="telefone"]').mask('(00) 00000-0000');
    $('input[name="contato"]').mask('(00) 00000-0000'); // Ou (00) 0000-0000 se for fixo

});
