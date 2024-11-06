
// https://developers.withhive.com/dev4/billing/subscriptions/
/* 
create javascript codes running on node.js environment that read in a HTML file, find 2 tables right after the heading section "expose-google-notification-popup", remove all classes from all HTML tags of this table, and add a new class called "notranslate" to the second column of every row of this table, and save this changed HTML document to an another HTML file. 
*/

/* 앞서 코파일럿 채팅으로 실행해서 얻은 결과까지도, 두 번째 코파일럿 채팅 실행 결과를 산출하는 데 반영한다. 그야말로 미쳤다. 
두 번째 실행에서는 파일 path까지 자동으로 인식하여 잡아주었다. 현재 js 파일에 주석으로 내가 작성한 파일 패스를 인식하여 활용한 것으로 보인다.

위 프롬프트는 잘못되었음. nextAll()은 sibling을 찾는데, 우리가 찾는 테이블은 h4 섹션의 sibling인 ul 객체의 children임. 그래서 아래와 같이 코드를 고쳤음
*/

const fs = require('fs');
const cheerio = require('cheerio');

// Read the HTML file
const html = fs.readFileSync('C:/Users/khy/Documents/workspace/dev_docs/ko/dev4/billing/subscriptions.html', 'utf8');

// Load the HTML into Cheerio
const $ = cheerio.load(html);

// Find the tables after the "expose-google-notification-popup" heading
const uls = $('#expose-google-notification-popup').nextAll('ul').slice(0, 2);

// Remove all classes from all HTML tags of these tables
uls.each((i, ul) => {
    function changeClass(table) {
        $(table).find('*').removeAttr('class');
        // Add a new class called "notranslate" to the second column of every row of these tables
        $(table).find('tr').each((i, row) => {
            $(row).find('td:nth-child(2)').addClass('notranslate');
        });
    }

    $(ul).children('table').each((i, table) => {
        changeClass(table);
    });
    
});

// Write the changed HTML document to another HTML file
fs.writeFileSync('C:/Users/khy/Documents/workspace/dev_docs/ko/dev4/billing/subscriptions-TMP.html', $.html());


