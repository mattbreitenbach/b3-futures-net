-- SCHEMA TEORICO DO BANCO DE DADOS, POREM NA PRATICA NAO FOI UTILIZADO.


CREATE DATABASE IF NOT EXISTS ajustes_bmf;

USE ajustes_bmf;

CREATE TABLE IF NOT EXISTS ajustes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_pregao DATE NOT NULL,
    mercadoria VARCHAR(50) NOT NULL,
    vencimento VARCHAR(3) NOT NULL,
	preco_ajuste_anterior DECIMAL(13, 4) NOT NULL, 
	preco_ajuste DECIMAL(13, 4) NOT NULL, 
	variacao DECIMAL(13, 4) NOT NULL, 
	valor_ajuste DECIMAL(13, 4) NOT NULL, 
);

