// FUNÇÃO RESPONSÁVEL PELAS ABAS DA BARRA LATERAL
function alternar(evt, tagName) {
    // Declaração de todas as variáveis
    var i, tabcontent, tablinks;
    // Recebe todos os elementos com a class="tabcontent" e oculta
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    // Recebe todos os elementos com a class="tablinks" e remove a class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    // Mostra a aba atual, e adiciona um class "active" ao link aberto pela aba
    document.getElementById(tagName).style.display = "flex";
    evt.currentTarget.className += " active";
}
// Recebe o elemento com o id="defaultOpen" e clica nele, definindo como a aba padrão
document.getElementById("defaultOpen").click();

// INSERÇÃO DE TEXTO ALTERNATIVO NOS LIVROS
var iAlt, imgAlt, captionAlt;
imgAlt = document.getElementById('Início').getElementsByTagName('img');
captionAlt = document.getElementsByTagName('figcaption');
for (iAlt = 0; iAlt < imgAlt.length; iAlt++) {
    imgAlt[iAlt].alt = `Livro ${captionAlt[iAlt].innerHTML}`
}
