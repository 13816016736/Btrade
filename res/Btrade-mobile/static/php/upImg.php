<?php
Header("Content-type: application/json");

$base64_string = $_POST['base64_string'];

$savename = uniqid().'.jpg'; // 后缀名没有做自动匹配，直接写死了
$savepath = '../assets/'.$savename; 
$image = base64_to_img( $base64_string, $savepath );
if($image){
    echo '{"status":1,"msg":"上传成功","url":"'.$image.'"}';
}else{
    echo '{"status":0,"msg":"上传失败"}';
} 
function base64_to_img( $base64_string, $output_file ) {
    $ifp = fopen( $output_file, "wb" ); 
    fwrite( $ifp, base64_decode( $base64_string) ); 
    fclose( $ifp ); 
    return( $output_file ); 
} 
?>