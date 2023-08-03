# Lembra do arquivo que criamos? Vamos importá-lo aqui
import pickle

# Flask é um microframework para criar aplicações web
from flask import Flask, render_template, request

# Instanciando a aplicação com a pasta de templates
app = Flask(__name__, template_folder='template', static_folder='template/assets')

# Treina lá, usa cá
# Aqui vamos carregar o modelo que treinamos
modelo_recsys = pickle.load(open('./models/modelo_recsys.pickle', 'rb'))
livros_df = pickle.load(open('./models/livros_df.pickle', 'rb'))
livros_por_usuario = pickle.load(open('./models/livro_por_usuario.pickle', 'rb'))


# Endpoint principal (home)
@app.route('/')
def home():
    return render_template("homepage.html")

# Endpoint para o formulário
@app.route('/livros')
def livros():
    return render_template("form.html")

# Endpoint que executa a classificação do cliente e retorna o resultado
@app.route('/recomendacoes', methods=['POST'])
def show_data():
    recomendacoes = []
    livro_buscado = "Não foi encontrado livros com esse nome"

    # Obtém o termo de pesquisa enviado pelo usuário
    livro = request.form['livro']

    # Filtra o DataFrame com base no termo de pesquisa
    resultados = livros_por_usuario[livros_por_usuario.index.str.contains(livro, case=False)]

    if len(resultados) > 0:
        resultado = resultados.index[0]

        livro_buscado = f'Livro buscado: {resultado}'

        try:
            posicao_resultado = livros_por_usuario.index.get_loc(resultado)
        except KeyError:
            resultado = resultados.iloc[1, 1]
            posicao_resultado = livros_por_usuario.index.get_loc(resultado)

        # Buscar os 6 "vizinhos" mais parecidos com o livro 1 do
        # Harry Potter
        quantidade_recomendacoes = 21

        distancias, indices = modelo_recsys.kneighbors(
            livros_por_usuario.iloc[posicao_resultado, :].values.reshape(1, -1), n_neighbors=quantidade_recomendacoes)

        for i in range(0, len(distancias.flatten())):
            if i == 0:
                pass # print('Recomendações para {0}:\n'.format(livro_por_usuario.index[posicao_harry_potter]))
            else:
                # Pegando o título da recomendação
                titulo_recomendacao = livros_por_usuario.index[indices.flatten()[i]]

                # Buscando a url da capa a partir do título (não temos mais o isbn, lembra?)
                titulo, url_capa = livros_df.loc[livros_df['titulo'] == titulo_recomendacao, ['titulo', 'url_capa']].values[
                    0]

                recomendacoes.append((titulo_recomendacao, url_capa))


    return render_template('result.html', recomendacoes=recomendacoes, titulo=livro_buscado)


# Roda a aplicação
if __name__ == "__main__":
    app.run(debug=True)
