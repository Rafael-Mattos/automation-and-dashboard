<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerador de Relatório</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }

        h1 {
            text-align: center;
            color: #333;
        }

        form {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }

        label {
            margin-bottom: 8px;
            color: #555;
        }

        input, button {
            margin-bottom: 16px;
            padding: 10px;
        }

        button {
            background-color: #4caf50;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        button:hover {
            background-color: #45a049;
        }

        .checkbox-group {
            display: flex;
            align-items: center;
        }

        .checkbox-group input[type="checkbox"] {
            margin-right: 8px;
            align-self: flex-start;
        }

        .checkbox-group label {
            align-self: flex-start;
        }
    </style>
</head>
<body>
    <form action="gerar_relatorio.php" method="post">
        <h1>Gerador de Relatório</h1>
        <label for="data_inicio">Data de Início:</label>
        <input type="date" id="data_inicio" name="data_inicio" required>
        <br>
        <label for="data_fim">Data de Fim:</label>
        <input type="date" id="data_fim" name="data_fim" style="margin-left: 11px;" required>

        <br>
        <br>

        <label>Status:</label>
        <br>
        <br>
        <div class="checkbox-group">
            <input type="checkbox" id="pendente" name="status[]" value="Pendente">
            <label for="pendente">Pendente</label>
        </div>

        <div class="checkbox-group">
            <input type="checkbox" id="finalizado" name="status[]" value="Finalizado">
            <label for="finalizado">Finalizado</label>
        </div>

        <br>

        <button type="submit" name="gerar_relatorio">Gerar Relatório</button>
    </form>
</body>
</html>
