import threading
import time
import logging
from database import DatabaseConnection
from business.numero_sorte import NumeroSorteBusiness
from business.cadastrar_nota import CadastrarNotaBusiness


class ThreadVerificacaoNotas:
    """
    Thread que verifica automaticamente notas validadas e processa saldo/números da sorte
    """

    def __init__(self):
        self.running = False
        self.thread = None
        self.db = DatabaseConnection()

    def iniciar_thread(self):
        """Iniciar thread de verificação"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._verificar_notas_loop,
                                           daemon=True)
            self.thread.start()
            logging.info("Thread de verificação de notas iniciada")

    def parar_thread(self):
        """Parar thread de verificação"""
        self.running = False
        if self.thread:
            self.thread.join()
            logging.info("Thread de verificação de notas parada")

    def _verificar_notas_loop(self):
        """Loop principal da thread - executa a cada 10 segundos"""
        while self.running:
            try:
                self._processar_notas_validadas()
                # Aguardar 10 segundos para verificação rápida
                time.sleep(10)
            except Exception as e:
                logging.error(f"Erro na thread de verificação: {e}")
                time.sleep(10)  # Aguardar mesmo em caso de erro

    def _processar_notas_validadas(self):
        """
        Processar notas validadas que ainda não foram somadas
        
        SQLs utilizadas:
        1. SELECT cpf, valor FROM tab_nota WHERE status = 1 AND somar = 1
        2. SELECT saldo FROM tab_cliente WHERE cpf = 'CPF'
        3. UPDATE tab_cliente SET saldo = 'NOVO_SALDO' WHERE cpf = 'CPF'
        4. UPDATE tab_nota SET somar = 0 WHERE cpf = 'CPF' AND status = 1 AND somar = 1
        """
        try:
            # Conectar ao banco
            conectado = self.db.connect()

            if not conectado:
                logging.warning(
                    "Não foi possível conectar ao banco para verificação de notas"
                )
                return

            # 1. Buscar notas validadas que ainda não foram somadas
            sql_notas = "SELECT cpf, valor FROM tab_nota WHERE status = 1 AND somar = 1"
            notas_para_processar = self.db.execute_select(sql_notas)

            if not notas_para_processar:
                # Não há notas para processar
                self.db.close()
                return

            # Agrupar por CPF para processar clientes
            clientes_notas = {}
            for cpf, valor in notas_para_processar:
                if cpf not in clientes_notas:
                    clientes_notas[cpf] = []
                clientes_notas[cpf].append(float(valor))

            logging.info(
                f"Processando {len(clientes_notas)} clientes com notas validadas"
            )

            # 2. Processar cada cliente
            for cpf, valores_notas in clientes_notas.items():
                self._processar_cliente(cpf, valores_notas)

            self.db.close()

        except Exception as e:
            logging.error(f"Erro ao processar notas validadas: {e}")
            try:
                self.db.close()
            except:
                pass

    def _processar_cliente(self, cpf, valores_notas):
        """
        Processar um cliente específico - gerar números e atualizar saldo restante
        Implementa controle de transação para garantir atomicidade
        """
        try:
            # Calcular total das notas validadas
            total_notas = sum(valores_notas)

            # 1. Buscar saldo atual do cliente
            sql_saldo = "SELECT ISNULL(saldo, 0) FROM tab_cliente WHERE cpf = ?"
            resultado_saldo = self.db.execute_select(sql_saldo, (cpf,))

            saldo_atual = 0
            if resultado_saldo and len(resultado_saldo) > 0:
                saldo_atual = float(resultado_saldo[0][0])

            # 2. Calcular novo saldo total
            novo_saldo_total = saldo_atual + total_notas

            # 3. Calcular quantos números deveria ter com o novo saldo
            quantidade_num = CadastrarNotaBusiness.calcular_numeros_sorte(
                novo_saldo_total)

            # 4. Calcular saldo restante (sobra dos múltiplos de R$ 20)
            saldo_restante = novo_saldo_total % 20

            # === INÍCIO DA TRANSAÇÃO ===
            # 5. Iniciar transação para garantir atomicidade
            self.db.execute_insert_update_delete("BEGIN TRANSACTION")
            
            try:
                # 6. Gerar números da sorte se necessário
                if quantidade_num > 0:
                    sucesso, mensagem = NumeroSorteBusiness.gerar_numeros_sorte(
                        cpf, quantidade_num, self.db)
                    if not sucesso:
                        raise Exception(f"Erro ao gerar números: {mensagem}")

                # 7. Atualizar saldo do cliente apenas com o valor restante
                sql_update_saldo = "UPDATE tab_cliente SET saldo = ? WHERE cpf = ?"
                resultado_saldo = self.db.execute_insert_update_delete(sql_update_saldo, (saldo_restante, cpf))
                if not resultado_saldo:
                    raise Exception("Falha ao atualizar saldo do cliente")

                # 8. Marcar notas como processadas (somar = 0)
                sql_update_notas = "UPDATE tab_nota SET somar = 0 WHERE cpf = ? AND status = 1 AND somar = 1"
                resultado_notas = self.db.execute_insert_update_delete(sql_update_notas, (cpf,))
                if not resultado_notas:
                    raise Exception("Falha ao marcar notas como processadas")

                # 9. Confirmar transação
                self.db.execute_insert_update_delete("COMMIT")

                logging.info(
                    f"Cliente {cpf}: {quantidade_num} números gerados, saldo restante R$ {saldo_restante:.2f}, {len(valores_notas)} notas processadas"
                )

            except Exception as transacao_erro:
                # Desfazer transação em caso de erro
                try:
                    self.db.execute_insert_update_delete("ROLLBACK")
                    logging.warning(f"Transação desfeita para cliente {cpf}: {transacao_erro}")
                except:
                    logging.error(f"Falha ao executar ROLLBACK para cliente {cpf}")
                raise transacao_erro

        except Exception as e:
            logging.error(f"Erro ao processar cliente {cpf}: {e}")


# Instância global da thread
thread_verificacao = ThreadVerificacaoNotas()
