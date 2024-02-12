<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Página de Login</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f4f4f4;
      margin: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }

    #login-container {
      background-color: #fff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      text-align: center;
    }

    #login-form input {
      width: 100%;
      padding: 10px;
      margin: 10px 0;
      box-sizing: border-box;
    }

    #login-button {
      background-color: #4caf50;
      color: #fff;
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
  </style>
</head>
<body>

<div id="login-container">
  <h2>Login</h2>
  <form id="login-form">
    <input type="email" id="email" placeholder="Email" required>
    <br>
    <input type="password" id="password" placeholder="Senha" required>
    <br>
    <button type="button" id="login-button">Login</button>
  </form>
</div>

<script>
  document.getElementById('login-button').addEventListener('click', function () {
    // Dados de login de exemplo
    const email = 'seuemail@email.com';
    const senha = '123456';

    // Obtendo os valores digitados pelo usuário
    const inputEmail = document.getElementById('email').value;
    const inputSenha = document.getElementById('password').value;

    // Verificando se os dados estão corretos
    if (inputEmail === email && inputSenha === senha) {
      // Redirecionando para a página "sistema.php"
      window.location.href = 'sistema.php';
    } else {
      alert('Login ou senha incorretos. Tente novamente.');
    }
  });
</script>

</body>
</html>
