/*
Navicat MySQL Data Transfer

Source Server         : localhost_3306
Source Server Version : 50617
Source Host           : localhost:3306
Source Database       : yaocai

Target Server Type    : MYSQL
Target Server Version : 50617
File Encoding         : 65001

Date: 2016-06-23 09:05:22
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for child_user
-- ----------------------------
DROP TABLE IF EXISTS `child_user`;
CREATE TABLE `child_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_user_id` int(11) NOT NULL,
  `child_user_id` int(11) NOT NULL,
  `acl` varchar(20) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '为了以后扩展子账号权限',
  `createtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of child_user
-- ----------------------------
INSERT INTO `child_user` VALUES ('17', '10', '4', '', '2016-06-23 08:57:30');
INSERT INTO `child_user` VALUES ('18', '10', '6', '', '2016-06-23 08:57:30');
INSERT INTO `child_user` VALUES ('19', '10', '311', '', '2016-06-23 08:57:30');
INSERT INTO `child_user` VALUES ('20', '10', '655', '', '2016-06-23 08:57:30');
INSERT INTO `child_user` VALUES ('21', '10', '605', '', '2016-06-23 08:57:30');
INSERT INTO `child_user` VALUES ('22', '10', '652', '', '2016-06-23 08:57:30');
INSERT INTO `child_user` VALUES ('23', '10', '538', '', '2016-06-23 08:57:30');
INSERT INTO `child_user` VALUES ('24', '10', '775', '', '2016-06-23 08:57:30');
INSERT INTO `child_user` VALUES ('25', '10', '848', '', '2016-06-23 08:57:30');
INSERT INTO `child_user` VALUES ('26', '1075', '10', '', '2016-06-23 09:04:16');
INSERT INTO `child_user` VALUES ('27', '1075', '4', '', '2016-06-23 09:04:16');
INSERT INTO `child_user` VALUES ('28', '1075', '6', '', '2016-06-23 09:04:16');
INSERT INTO `child_user` VALUES ('29', '1075', '311', '', '2016-06-23 09:04:16');
INSERT INTO `child_user` VALUES ('30', '1075', '655', '', '2016-06-23 09:04:16');
INSERT INTO `child_user` VALUES ('31', '1075', '605', '', '2016-06-23 09:04:16');
INSERT INTO `child_user` VALUES ('32', '1075', '652', '', '2016-06-23 09:04:16');
INSERT INTO `child_user` VALUES ('33', '1075', '538', '', '2016-06-23 09:04:16');
INSERT INTO `child_user` VALUES ('34', '1075', '775', '', '2016-06-23 09:04:16');
INSERT INTO `child_user` VALUES ('35', '1075', '848', '', '2016-06-23 09:04:16');
