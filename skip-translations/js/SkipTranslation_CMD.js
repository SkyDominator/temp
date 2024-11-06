/**
 * This script allows the user to skip translation for specific tables in an HTML file.
 * It prompts the user to enter the input file path, directHeadingId for the table, sequence of seeking table,
 * colNo, and then modifies the HTML file by adding a "notranslate" class to the specified columns of the tables.
 * The modified HTML is then saved to the same file.
 */

const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');
const readline = require('readline');

// Read the HTML file
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

let lastInputFile = ''; // Variable to store the last inputFile

// Load the lastInputFile from the data file if it exists
const dataFilePath = path.join(__dirname, 'lastInputFile.txt');
if (fs.existsSync(dataFilePath)) {
    lastInputFile = fs.readFileSync(dataFilePath, 'utf8');
}

rl.question('Enter the input file path (input "LAST" if you are working with the last saved file): ', (inputFile) => {
    
    if (inputFile.toUpperCase() === 'LAST') {
        inputFile = lastInputFile; // Use the last saved inputFile
    } else {
        lastInputFile = inputFile; // Save the current inputFile as the last inputFile

        // Save the lastInputFile to the data file
        fs.writeFileSync(dataFilePath, lastInputFile);
    }

    rl.question('Enter directHeadingId for the table: ', (directHeadingId) => {
        rl.question('Enter the sequence of seeking table (comma-separated numbers "1,2" or a single number "1"): ', (sequence) => {
            rl.question('Enter the sequence of seeking colNo (comma-separated numbers "1,2" or a single number "1"): ', (colNo) => {
                rl.close();

                const html = fs.readFileSync(inputFile, 'utf8');

                // Load the HTML into Cheerio
                const $ = cheerio.load(html);

                /**
                 * Finds the table with the specified directHeadingId and sequence.
                 * @param {string} _directHeadingId - The directHeadingId of the table to find.
                 * @param {number} _sequence - The sequence of the table to find.
                 * @returns {Cheerio} The Cheerio object representing the found table.
                 */
                function findTable(_directHeadingId, _sequence) {
                    const table = $('#' + _directHeadingId).nextAll('table').slice(0, _sequence);
                    return table;
                }

                /**
                 * Adds the "notranslate" class to the specified column of every row in the table.
                 * @param {Cheerio} _table - The Cheerio object representing the table.
                 * @param {number} _colNoSeq - The column number to add the class to.
                 */
                function changeClass(_table, _colNoSeq) {
                    // 테이블에 있는 모든 class 속성 제거
                    // // Remove all existing class attributes from the table
                    // $(_table).find('*').removeAttr('class');

                    /* 테이블에 _colNo번째 열에 해당하는 클래스 붙여서 번역 skip 처리 */

                    let _colNo;
                    let _class;

                    _colNoSeq = _colNoSeq.split(',').map(Number); // Convert _colNoSeq to an array of numbers

                    for (let i = 0; i < _colNoSeq.length; i++) {
                        _colNo = _colNoSeq[i];
                        _class = 'cCol' + _colNo;
                        $(_table).addClass(_class);
                    }
                    // /* _colNo번째 열에 있는 모든 행에 번역 skip 처리 */
                    // // Add a new class called "notranslate" to the _colNo column of every row of these tables
                    // $(_table).find('tr').each((i, row) => {
                    //     $(row).find(`td:nth-child(${_colNo})`).addClass('notranslate');
                    // });
                }

                const sequenceArray = sequence.split(',').map(Number); // Convert the sequence input to an array of numbers

                sequenceArray.forEach((seq) => {
                    const table = findTable(directHeadingId, seq);
                    if (!table) {
                        console.log('No table found.');
                        process.exit();
                    }
                    changeClass(table, colNo);
                });

                // Remove head and body tags
                let newHTML = $.html();
                newHTML = newHTML.replace('<html>', '');
                newHTML = newHTML.replace('</html>', '');
                newHTML = newHTML.replace('<head>', '');
                newHTML = newHTML.replace('</head>', '');
                newHTML = newHTML.replace('<body>', '');
                newHTML = newHTML.replace('</body>', '');

                // Replace all special characters
                newHTML = newHTML.replace(/&amp;/g, '&');
                newHTML = newHTML.replace(/&gt;/g, '>');
                newHTML = newHTML.replace(/&lt/g, '<');

                newHTML = newHTML.trim();

                // Write the changed HTML document to another HTML file
                const outputFile = inputFile;
                fs.writeFileSync(outputFile, newHTML);
                console.log(`Done!`);
            });
        });
    });
});


