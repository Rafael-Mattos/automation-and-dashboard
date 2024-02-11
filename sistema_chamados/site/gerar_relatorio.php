<?php
if (isset($_POST['gerar_relatorio'])) {
    // Recupere os dados do formulário
    $dataInicio = $_POST['data_inicio'];
    $dataFim = $_POST['data_fim'];
    $status = isset($_POST['status']) ? $_POST['status'] : [];

    // Simule a geração do relatório (neste exemplo, só redireciona para o arquivo CSV pré-preparado)
    $csvFilePath = 'dados/relatorio.csv';

    if (file_exists($csvFilePath)) {
        // Adiciona um sufixo com a data e hora no nome do arquivo baixado
        $downloadFileName = 'relatorio_' . date('Ymd_His') . '.csv';

        header('Content-Type: text/csv');
        header('Content-Disposition: attachment; filename=' . $downloadFileName);
        readfile($csvFilePath);
        exit;
    } else {
        echo "Arquivo CSV não encontrado.";
    }
}
?>
