$(document).ready(function() {
    // Lógica AJAX para carregar bairros
    var cidadeSelect = $('#id_cidade');
    var bairroSelect = $('#id_bairro');

    function loadBairros(cidadeId, urlEndpoint) {
        if (cidadeId && urlEndpoint) {
            $.ajax({
                url: urlEndpoint,
                data: {
                    'cidade_id': cidadeId
                },
                dataType: 'json',
                success: function (data) {
                    bairroSelect.empty();
                    bairroSelect.append($('<option value="">Todos os Bairros</option>'));
                    $.each(data, function (key, value) {
                        bairroSelect.append($('<option></option>').val(value.id).text(value.nome_bairro));
                    });
                }
            });
        } else {
            bairroSelect.empty();
            bairroSelect.append($('<option value="">Todos os Bairros</option>'));
        }
    }

    // Inicializa bairros se cidade já estiver selecionada
    if (cidadeSelect.val()) {
        var urlEndpoint = cidadeSelect.data('ajax-url');
        loadBairros(cidadeSelect.val(), urlEndpoint);
    }

    // Event listener para mudança de cidade
    cidadeSelect.change(function () {
        var cidadeId = $(this).val();
        var urlEndpoint = $(this).data('ajax-url');
        loadBairros(cidadeId, urlEndpoint);
    });

    // Script para lidar com os botões de exportação
    $('.export-btn').on('click', function() {
        const buttonName = $(this).attr('name');
        const mainForm = $('#main-filter-form');

        const formData = mainForm.serializeArray();
        let selectedColumns = [];

        // Adiciona apenas as colunas selecionadas
        $('input[name="columns"]:checked').each(function() {
            selectedColumns.push($(this).val());
        });

        // Constrói a URL manualmente para garantir a formatação correta
        let urlParams = [];

        $.each(formData, function(i, field){
            if (field.name !== 'columns') {
                urlParams.push(`${field.name}=${encodeURIComponent(field.value)}`);
            }
        });

        selectedColumns.forEach(column => {
            urlParams.push(`columns=${column}`);
        });

        urlParams.push(`${buttonName}=1`);

        window.location.href = `?${urlParams.join('&')}`;
    });

    // Validação de formulário - garantir que pelo menos uma coluna seja selecionada
    $('#main-filter-form').on('submit', function(e) {
        const checkedColumns = $('input[name="columns"]:checked').length;
        if (checkedColumns === 0) {
            e.preventDefault();
            alert('Por favor, selecione pelo menos uma coluna para exibir no relatório.');
            return false;
        }
    });

    // Auto-selecionar colunas padrão se nenhuma estiver selecionada
    if ($('input[name="columns"]:checked').length === 0) {
        $('input[name="columns"][value="nome"]').prop('checked', true);
        $('input[name="columns"][value="telefone"]').prop('checked', true);
        $('input[name="columns"][value="cidade"]').prop('checked', true);
    }
});