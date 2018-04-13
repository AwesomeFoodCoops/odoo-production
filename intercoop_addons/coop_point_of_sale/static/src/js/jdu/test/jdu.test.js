'use strict';

const jdu = require('../jdu');

let paragraph = "L'avantage d'utiliser le lorem ipsum est bien Ã©videmment de pouvoir crÃ©er des maquettes ou de remplir un" +
    " site internet de contenus qui prÃ©sentent un rendu s'approchant un maximum du rendu final. \n Par dÃ©faut lorem" +
    " ipsum ne contient pas d'accent ni de caractÃ¨res spÃ©ciaux contrairement Ã  la langue franÃ§aise qui en contient" +
    " beaucoup. C'est sur ce critÃ¨re que nous proposons une solution avec cet outil qui gÃ©nÃ©rant du faux-texte lorem" +
    " ipsum mais avec en plus, des caractÃ¨res spÃ©ciaux tel que les accents ou certains symboles utiles pour la langue" +
    " franÃ§aise. \n L'utilisation du lorem standard est facile dâ€™utilisation mais lorsque le futur client utilisera" +
    " votre logiciel il se peut que certains caractÃ¨res spÃ©ciaux ou qu'un accent ne soient pas codÃ©s correctement." +
    " \n Cette page a pour but donc de pouvoir perdre le moins de temps possible et donc de tester directement si tous" +
    " les encodages de base de donnÃ©e ou des sites sont les bons de plus il permet de rÃ©cuperer un code css avec le" +
    " texte formatÃ© !";

let noDiacriticsParagraph = "L'avantage d'utiliser le lorem ipsum est bien A©videmment de pouvoir crA©er des maquettes ou" +
    " de remplir un site internet de contenus qui prA©sentent un rendu s'approchant un maximum du rendu final. \n Par" +
    " dA©faut lorem ipsum ne contient pas d'accent ni de caractA¨res spA©ciaux contrairement A  la langue franA§aise qui" +
    " en contient beaucoup. C'est sur ce critA¨re que nous proposons une solution avec cet outil qui gA©nA©rant du" +
    " faux-texte lorem ipsum mais avec en plus, des caractA¨res spA©ciaux tel que les accents ou certains symboles" +
    " utiles pour la langue franA§aise. \n L'utilisation du lorem standard est facile da€™utilisation mais lorsque le" +
    " futur client utilisera votre logiciel il se peut que certains caractA¨res spA©ciaux ou qu'un accent ne soient" +
    " pas codA©s correctement. \n Cette page a pour but donc de pouvoir perdre le moins de temps possible et donc de" +
    " tester directement si tous les encodages de base de donnA©e ou des sites sont les bons de plus il permet de" +
    " rA©cuperer un code css avec le texte formatA© !";

var latinString = "This is in Latin";
var nonLatinString = "This is not in LÃtin";

test('remove diacritics', () => {
    expect(jdu.replace(paragraph)).toEqual(noDiacriticsParagraph);
});

test('isLatin', () => {
    expect(jdu.isLatin(latinString)).toBe(true);
    expect(jdu.isLatin(nonLatinString)).toBe(false);
});