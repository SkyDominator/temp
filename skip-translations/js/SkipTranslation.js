const fs = require('fs');
const cheerio = require('cheerio');

// Read the HTML file
const inputFile = 'C:/Users/khy/Documents/workspace/dev_docs/en/develop/authv4/idp-connect-helper.html'
const outputFile = inputFile.replace('.html', '-TMP.html');

// CHOOSE OPTIONS
const directHeadingId = 'idpconnect-guide-text';
const sequence = 1; // 1부터 시작
const colNo = [1,2]; // 1부터 시작

const html = fs.readFileSync(inputFile, 'utf8');

// Load the HTML into Cheerio
const $ = cheerio.load(html);

function findTable(_directHeadingId, _sequence) {
    return $('#'+_directHeadingId).nextAll('table').slice(0, _sequence);
    // $('#'+directHeadingId).nextAll('ul').children('table');
}

function changeClass(_table, _colNoSeq) {
    // // 테이블에 기존 설정된 클래스 속성 모두 제거
    // $(_table).find('*').removeAttr('class');

    /* 테이블에 _colNo번째 열에 해당하는 클래스 붙여서 번역 skip 처리 */
    let _colNo;
    let _class;
    for(let i = 0; i < _colNoSeq.length; i++){
        _colNo = _colNoSeq[i];
        _class = 'cCol' + _colNo;
        $(_table).addClass(_class);
    }

    // // Add a new class called "notranslate" to the second column of every row of these tables
    // $(_table).find('tr').each((i, row) => {
    //     $(row).find(`td:nth-child(${_colNo})`).addClass('notranslate');
    // });
}

// function findTable() {
//     const h4 = $('h4').filter((i, el) => {
//         return $(el).text().trim() === 'expose-google-notification-popup';
//     });
//     return h4.next('ul').children('table');
// }

const table = findTable(directHeadingId, sequence)
changeClass(table, colNo)

// head와 body 제거
let newHTML = $.html()
newHTML = newHTML.replace('<html>', '');
newHTML = newHTML.replace('</html>', '');
newHTML = newHTML.replace('<head>', '');
newHTML = newHTML.replace('</head>', '');
newHTML = newHTML.replace('<body>', '');
newHTML = newHTML.replace('</body>', '');
newHTML = newHTML.trim()

// Write the changed HTML document to another HTML file
fs.writeFileSync(outputFile, newHTML);




