update users set openid="";
update users set openid2="";

ALTER TABLE `supplier`
ADD COLUMN `yaoyy_status`  int(5) NULL AFTER `maxpush`;

