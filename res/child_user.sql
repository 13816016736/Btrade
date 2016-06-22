/*
Navicat MySQL Data Transfer

Source Server         : localhost_3306
Source Server Version : 50617
Source Host           : localhost:3306
Source Database       : yaocai

Target Server Type    : MYSQL
Target Server Version : 50617
File Encoding         : 65001

Date: 2016-06-22 14:06:35
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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of child_user
-- ----------------------------
INSERT INTO `child_user` VALUES ('9', '10', '4', '', '2016-06-22 12:12:26');
INSERT INTO `child_user` VALUES ('10', '10', '6', '', '2016-06-22 12:12:26');
INSERT INTO `child_user` VALUES ('11', '10', '311', '', '2016-06-22 12:12:26');
INSERT INTO `child_user` VALUES ('12', '10', '655', '', '2016-06-22 12:12:26');
INSERT INTO `child_user` VALUES ('13', '10', '605', '', '2016-06-22 12:12:26');
INSERT INTO `child_user` VALUES ('14', '10', '652', '', '2016-06-22 12:12:26');
INSERT INTO `child_user` VALUES ('15', '10', '538', '', '2016-06-22 12:12:26');
INSERT INTO `child_user` VALUES ('16', '10', '775', '', '2016-06-22 12:12:26');
