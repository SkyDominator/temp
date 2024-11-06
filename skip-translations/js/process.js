
// https://developers.withhive.com/dev4/billing/iapv4-purchase/#inapp_reject_text
/* 
create javascript codes running on node.js environment that read in a HTML file, find a table right after the heading section "inapp_reject_text", remove all classes from all HTML tags of this table, and add a new class called "notranslate" to the second column of every row of this table, and save this changed HTML document to an another HTML file. 
*/

const fs = require('fs');
const cheerio = require('cheerio');

// Read the HTML file
const html = fs.readFileSync('C:/Users/khy/Documents/workspace/dev_docs/ko/dev4/billing/iapv4-purchase.html', 'utf8');

// Load the HTML into Cheerio
const $ = cheerio.load(html);

// Find the table after the "inapp_reject_text" heading
const table = $('#inapp_reject_text').next('table');

// Remove all classes from all HTML tags of this table
table.find('*').removeAttr('class');

// Add a new class called "notranslate" to the second column of every row of this table
table.find('tr').each((i, row) => {
    $(row).find('td:nth-child(2)').addClass('notranslate');
});

// Write the changed HTML document to another HTML file
fs.writeFileSync('C:/Users/khy/Documents/workspace/dev_docs/ko/dev4/billing/iapv4-purchase-TMP.html', $.html());



