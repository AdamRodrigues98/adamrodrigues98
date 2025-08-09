CREATE DATABASE StackOverflow2013
    ON (FILENAME = 'C:\StackOverflow2013\StackOverflow2013_1.mdf'),
    (FILENAME = 'C:\StackOverflow2013\StackOverflow2013_2.ndf'),
    (FILENAME = 'C:\StackOverflow2013\StackOverflow2013_3.ndf'),
	(FILENAME = 'C:\StackOverflow2013\StackOverflow2013_4.ndf')
	LOG ON (FILENAME = 'C:\StackOverflow2013\StackOverflow2013_log.ldf')
FOR ATTACH;

