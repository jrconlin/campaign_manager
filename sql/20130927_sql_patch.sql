CREATE TABLE if not exists `users` (
  `id` varchar(32) NOT NULL DEFAULT '',
  `email` varchar(100) NOT NULL,
  `sponsor` varchar(100) DEFAULT NULL,
  `date` int(11) DEFAULT NULL,
  `level` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('0','jconlin@mozilla.com',NULL,1380154102,0),('1085eb386c2940a9a59c8f93e7655a41','bwong@mozilla.com','jconlin@mozilla.com',1380238317,0),('91becec273e14ff3ae4228fc3d0a6509','jmontano@mozilla.com','jconlin@mozilla.com',1380238334,0),('a91f69ef18b04d018470d8ca28d0997e','elancaster@mozilla.com','jconlin@mozilla.com',1380238948,0) On Duplicate Key Update `date` = unix_timestamp();
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

Lock tables `campaigns` write;
Alter table campaigns add status integer;
unlock tables;
