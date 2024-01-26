<?php
error_reporting(E_ALL & ~E_WARNING & ~E_NOTICE);
include("currency.php");

$resultLink = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $region = $_POST["region"];
    $amount = $_POST["amount"];

    $isoName = $countryData[$region]["ISO"];
    $rate = $countryData[$region]["toTWD"];

    $convertedAmount = $amount * $rate ?: $amount;

    $htmlContent = "<html><body>";
    $htmlContent .= "<h1> Exchange result </h1>";
    $htmlContent .= "<p>{$amount} TWD = {$convertedAmount} {$isoName}</p>";
    $htmlContent .= "<a href='/'>Back to Home</a></body></html>";

    $filePath = "upload/" . md5(uniqid()) . "." . $isoName;
    file_put_contents($filePath, $htmlContent);

    $resultLink = "<a href='" . $filePath . "'> 👁️ exchange result</a>";
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>🪙Exchange Station</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tocas/4.2.5/tocas.min.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tocas/4.2.5/tocas.min.js"></script>

    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet" />

</head>
<body>
    <div class="ts-segment">
        <div class="ts-app-navbar is-fluid">
            <a class="item">
                <div class="ts-icon is-house-icon"></div>
                <div class="label">Home</div>
            </a>
        </div>
    </div>
    <br>
    <br>
    <div class="ts-container is-very-narrow">
    <fieldset class="ts-fieldset">
    <legend>🪙Exchange Station</legend>
        <form action="" method="post">
            <label for="region">🌏Region</label>
            <div class="ts-select">
                <select name="region" id="region">
                    <?php foreach ($countryData as $region => $data): ?>
                        <option value="<?php echo $region; ?>"><?php echo $region; ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            <br>
            <br>
            <div class="ts-input is-labeled">
                <span class="label">💵Amount </span>
                <input type="text" id="amount" name="amount" required>
                <span class="label">TWD</span>
            </div>
            <br>
            <button class="ts-button">Submit</button>
        </form>
        <?php
        if ($resultLink) {
            echo $resultLink;
        }
        ?>
        </fieldset>
    </div>
</body>
</html>
