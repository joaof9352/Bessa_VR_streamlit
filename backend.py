from constants import classificacao, resultados

class ClassificacaoCalculator:
    def __init__(self):
        self.classificacao = classificacao
        self.resultados = resultados

    def calcular_classificacao(self, jogos_realizados):
        # Converte a lista de classificação em um dicionário para facilitar a manipulação
        class_dict = {nome: {"Pontos": pontos, "Vitórias": vitorias, "GM": gm, "GS": gs} for nome, pontos, vitorias, gm, gs in self.classificacao}
        
        # Atualiza o dicionário com os resultados dos jogos
        for casa, fora, gols_casa, gols_fora in jogos_realizados:
            if gols_casa > gols_fora:  # Vitória do time da casa
                class_dict[casa]["Pontos"] += 3
                class_dict[casa]["Vitórias"] += 1
            elif gols_casa < gols_fora:  # Vitória do time visitante
                class_dict[fora]["Pontos"] += 3
                class_dict[fora]["Vitórias"] += 1
            else:  # Empate
                class_dict[casa]["Pontos"] += 1
                class_dict[fora]["Pontos"] += 1
                
            class_dict[casa]["GM"] += gols_casa
            class_dict[casa]["GS"] += gols_fora
            class_dict[fora]["GM"] += gols_fora
            class_dict[fora]["GS"] += gols_casa
            
        return class_dict
            
    def primeiro_criterio(self, equipas_empatadas):
        classificacao_miniliga = {x: 0 for x in equipas_empatadas}
        for e_casa, e_fora, g_c, g_f in filter(lambda x: x[0] in equipas_empatadas and x[1] in equipas_empatadas, self.resultados):
            if g_c > g_f:
                classificacao_miniliga[e_casa] += 3
            elif g_c < g_f:
                classificacao_miniliga[e_fora] += 3
            else:
                classificacao_miniliga[e_casa] += 1
                classificacao_miniliga[e_fora] += 1

        list_sorted = sorted(classificacao_miniliga.items(), key=lambda x: x[1], reverse=True)
        return list_sorted

    def segundo_criterio(self, equipas_empatadas):
        golos_miniliga = {x: (0,0) for x in equipas_empatadas}
        for e_casa, e_fora, g_c, g_f in filter(lambda x: x[0] in equipas_empatadas and x[1] in equipas_empatadas, self.resultados):
            golos_miniliga[e_casa] = (golos_miniliga[e_casa][0] + g_c, golos_miniliga[e_casa][1] + g_f)
            golos_miniliga[e_fora] = (golos_miniliga[e_fora][0] + g_f, golos_miniliga[e_fora][1] + g_c)
        
        return [(k, v[0] - v[1]) for k, v in golos_miniliga.items()]

    def terceiro_criterio(self, equipas_empatadas):
        """
        Terceiro critério de desempate baseado no maior número de gols marcados fora de casa
        nas partidas entre as equipes empatadas.
        """
        golos_miniliga = {x: 0 for x in equipas_empatadas}
        for e_casa, e_fora, g_c, g_f in filter(lambda x: x[0] in equipas_empatadas and x[1] in equipas_empatadas, resultados):
            golos_miniliga[e_fora] += g_f

        return sorted(golos_miniliga.items(), key=lambda x: x[1], reverse=True)

    def quarto_criterio(self, classificacao):
        """
        Quarto critério de desempate baseado na melhor diferença de gols na classificação geral.
        """
        return sorted(classificacao.items(), key=lambda x: (x[1]['GM'] - x[1]['GS']), reverse=True)

    def aplicar_criterios_desempate(self, equipas_empatadas):
        """
        Aplica os critérios de desempate sequencialmente até resolver todos os empates.
        """
        # Aplica o primeiro critério
        resultado_primeiro = self.primeiro_criterio(equipas_empatadas)
        if len(set([pontos for _, pontos in resultado_primeiro])) == len(equipas_empatadas):
            return resultado_primeiro

        # Prepara para o segundo critério, se necessário
        equipas_para_segundo_criterio = [e for e, _ in resultado_primeiro]
        resultado_segundo = self.segundo_criterio(equipas_para_segundo_criterio)
        if len(set([saldo for _, saldo in resultado_segundo])) == len(equipas_empatadas):
            return resultado_segundo

        # Prepara para o terceiro critério, se necessário
        equipas_para_terceiro_criterio = [e for e, _ in resultado_segundo]
        resultado_terceiro = self.terceiro_criterio(equipas_para_terceiro_criterio)
        return resultado_terceiro

    def calcular_classificacao_final(self, jogos_a_realizar):
        
        # Atualiza a classificação com os resultados dos jogos a realizar
        classificacao_atualizada = self.calcular_classificacao(jogos_a_realizar)
        self.resultados += jogos_a_realizar

        # Calcula a classificação final considerando os desempates necessários
        classificacao_final = {}
        for equipe, dados in classificacao_atualizada.items():
            classificacao_final[equipe] = dados

        # Identifica grupos de equipes empatadas em pontos para aplicar os critérios de desempate
        equipes_ordenadas_por_pontos = sorted(classificacao_atualizada.items(), key=lambda x: x[1]['Pontos'], reverse=True)
        i = 0
        while i < len(equipes_ordenadas_por_pontos):
            equipe_atual, _ = equipes_ordenadas_por_pontos[i]
            equipas_empatadas = [equipe_atual]

            # Encontra equipes com o mesmo número de pontos
            j = i + 1
            while j < len(equipes_ordenadas_por_pontos) and equipes_ordenadas_por_pontos[i][1]['Pontos'] == equipes_ordenadas_por_pontos[j][1]['Pontos']:
                equipas_empatadas.append(equipes_ordenadas_por_pontos[j][0])
                j += 1

            # Se houver empates, aplica os critérios de desempate
            if len(equipas_empatadas) > 1:
                resultado_desempate = self.aplicar_criterios_desempate(equipas_empatadas)
                for equipe, valor in resultado_desempate:
                    # Atualiza a classificação final com o resultado do desempate
                    if isinstance(valor, int):  # Para critérios que retornam um valor numérico
                        classificacao_final[equipe]['Desempate'] = valor
                    else:  # Para critérios que já ajustam a classificação diretamente
                        classificacao_final[equipe] = classificacao_atualizada[equipe]

            i = j  # Avança para o próximo grupo de equipes

        return sorted(classificacao_final.items(), key=lambda x: (x[1]['Pontos'], x[1].get('Desempate', 0)), reverse=True)[1:]
