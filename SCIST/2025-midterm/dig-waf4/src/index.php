<!DOCTYPE html>
<html>
  <head>
    <title>Dig</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Mono&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Mono:wght@700&display=swap" rel="stylesheet">
    <style>
      body {
        font-family: 'Noto Sans Mono', monospace;
      }
      .btn {
        color: white;
        background-color: rgb(0, 143, 48);
        font-size: 16px;
        padding: 10px 28px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        margin-top: 5px;
        margin-left: 5px;
        box-shadow: 5px 5px 0 rgba(0,0,0,0.5);
      }
      .btn:hover {
        background-color: rgb(2, 121, 41);
      }
      .btn:active {
        margin-top: 10px;
        margin-left: 10px;
        box-shadow: 0 0 0 rgba(0,0,0,1);
      }
    </style>
  </head>
    <h1>Dig waf 4⛏️</h1>
    <form method="POST">
        <div>
            <input type="text" name="name" placeholder="example.com" id="hostname" value="<?= $_POST[
                "name"
            ] ?? "" ?>">
        </div>
        <button class="btn">
            dig!
        </button>
    </form>
    <br>
    <?php if (isset($_POST["name"])): ?>
        <p>
            <p>dig result:</p>
            <pre>
              <?php
              system($_POST["name"]);
              $blacklist = [
                  "|",
                  "&",
                  ";",
                  ">",
                  "<",
                  "\n",
                  "\t",
                  "{",
                  "}",
                  ",",
                  "`",
                  "f",
                  "l",
                  "a",
                  "g",
                  " ",
              ];
              $is_bad = false;
              foreach ($blacklist as $bad_word) {
                  if (strpos($_POST["name"], $bad_word) !== false) {
                      $is_bad = true;
                  }
              }

              if ($is_bad) {
                  echo "BAD HACKER!!!";
              } else {
                  system("dig '" . $_POST["name"] . "'");
              }
              ?>
            </pre>
    </p>
    <?php endif; ?>
    <hr>
    <div>
        dig '<span style="color: red;" id="command"></span>';
    </div>

    <script>
        window.onload = hostname.oninput = () => command.textContent = hostname.value;
    </script>

    <hr>
    <div style="display: inline-block;background-color: rgba(0,0,0,0.1);"><?php highlight_file(
        __FILE__
    ); ?></div>
</html>
