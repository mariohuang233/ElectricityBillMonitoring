

<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head><meta charset="utf-8" /><title>
	辰域智控系统
</title><meta http-equiv="X-UA-Compatible" content="IE=edge" /><meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" /><link rel="stylesheet" href="//www.storage.cnyiot.com/sys/wap/css/weui.min.css" /><link rel="stylesheet" href="//www.storage.cnyiot.com/sys/wap/css/jquery-weui.min.css" />
 <script src="//www.storage.cnyiot.com/sys/wap/js/jquery-2.2.4.min.js"></script> 
<script src="//www.storage.cnyiot.com/sys/wap/js/jquery-weui.min.js"></script>
     
    <script src="//www.storage.cnyiot.com/sys/wap/js/jweixin-1.6.0.js"></script>

    <link rel="shortcut icon" href="//www.storage.cnyiot.com/sys/web/img/favicon.ico" type="image/x-icon" />
    <script>
        if (window.location.href.toString().toLocaleLowerCase().indexOf("www.cnyiot.com") > -1) {
            alert("二维码过旧，请联系管理员重新生成二维码。以免影响使用");
        } 
        if (location.href.indexOf("&by") < 0) {
            var useragent = navigator.userAgent.toLowerCase();

            if (useragent.match(/MicroMessenger/i) == 'micromessenger') {
                location.replace(location.href.replace('www.native.', 'www.wap.') + '&by=wx');
            }
            else if (useragent.match(/AlipayClient/i) == 'alipayclient') {
                location.replace(location.href.replace('www.native.', 'www.wap.') + '&by=ali');
            }
            else {
                var sUserAgent = navigator.userAgent.toLowerCase();
                var bIsIpad = sUserAgent.match(/ipad/i) == "ipad";
                var bIsIphoneOs = sUserAgent.match(/iphone os/i) == "iphone os";
                var bIsMidp = sUserAgent.match(/midp/i) == "midp";
                var bIsUc7 = sUserAgent.match(/rv:1.2.3.4/i) == "rv:1.2.3.4";
                var bIsUc = sUserAgent.match(/ucweb/i) == "ucweb" || sUserAgent.match(/ucbrowser/i) == "ucbrowser";
                var bIsAndroid = sUserAgent.match(/android/i) == "android";
                var bIsCE = sUserAgent.match(/windows ce/i) == "windows ce";
                var bIsWM = sUserAgent.match(/windows mobile/i) == "windows mobile";
                if (bIsIpad || bIsIphoneOs || bIsMidp || bIsUc7 || bIsUc || bIsAndroid || bIsCE || bIsWM) {
                    location.replace(location.href.replace('www.native.', 'www.wap.') + '&by=a');
                } else {
                    $.alert('本浏览器暂不支持');
                }
            }
        }
    </script>
     
</head>
  
<body>
     <div id="wxOpenInAPP" class="wexin-launch-btn" style=" text-align:center;padding-top:40%">  </div>  
</body>
        
</html>
