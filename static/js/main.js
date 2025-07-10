$(document).ready(function(){
    // Aplica a máscara aos campos de telefone
    $('input[name="telefone"]').mask('(00) 00000-0000');

    // Aplica a máscara ao campo de contato (para colaborador)
    $('input[name="contato"]').mask('(00) 00000-0000'); 
});
