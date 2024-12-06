DROP TABLE IF EXISTS fakelog;

CREATE TABLE fakelog (
    id INTEGER PRIMARY KEY,
    context TEXT
);

INSERT INTO fakelog (id, context) VALUES
('0', 'FAKE | ping -r, 致命錯誤, 必須為選項 -r 提供值。'),
('1', 'FAKE | ping -n, 致命錯誤, 必須為選項 -n 提供值。'),
('2', 'FAKE | confj4ing, 致命錯誤, "confj4ing" 不是內部或外部命令、可執行的程式或批次檔。'),
('3', 'FAKE | confing, 致命錯誤, "confing" 不是內部或外部命令、可執行的程式或批次檔。'),
('4', 'FAKE | hkiuyrdg, 致命錯誤, "hkiuyrdg" 不是內部或外部命令、可執行的程式或批次檔。'),
('5', 'FAKE | m,lhfghfdx48478, 致命錯誤, "m" 不是內部或外部命令、可執行的程式或批次檔。');

DROP TABLE IF EXISTS secret_NEEDCHANGE;

CREATE TABLE secret_NEEDCHANGE (
    id INTEGER PRIMARY KEY,
    context TEXT
);

INSERT INTO secret_NEEDCHANGE (id, context) VALUES
('555', 'FLAG');
