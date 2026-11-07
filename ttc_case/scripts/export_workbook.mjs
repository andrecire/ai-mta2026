import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.resolve(root, '..', 'outputs', 'ttc_workshop');
const previewDir = path.join(root, 'instructor', 'previews');
await fs.mkdir(output, {recursive: true});
await fs.mkdir(previewDir, {recursive: true});
const data = JSON.parse(await fs.readFile(path.join(root, 'instructor', 'workbook_data.json'), 'utf8'));
const wb = Workbook.create();
const source = 'Source: City of Toronto / TTC - https://open.toronto.ca/dataset/ttc-subway-delay-data/';
const fields = ['date', 'day_of_week', 'station_id', 'station', 'time_window', 'log_entry_count', 'positive_delay_count', 'has_recorded_delay', 'recorded_delay_minutes'];

function addTable(name, title, note, headers, rows, widths) {
  const sheet = wb.worksheets.add(name);
  sheet.showGridLines = false;
  const n = rows.length + 6;
  const body = sheet.getRangeByIndexes(0, 0, n, headers.length);
  body.format.font = {name: 'Arial', size: 10, color: '#242424'};
  body.format.rowHeight = 19;
  body.format.verticalAlignment = 'center';
  sheet.getRange('A2').values = [[title]];
  sheet.getRange('A2').format.font = {name: 'Arial', size: 14, bold: true, color: '#292929'};
  sheet.getRange('A2').format.rowHeight = 25;
  sheet.getRange('A3').values = [[source]];
  sheet.getRange('A3').format.font = {name: 'Arial', size: 10, color: '#555555'};
  sheet.getRange('A4').values = [[note]];
  sheet.getRange('A4').format.font = {name: 'Arial', size: 10, italic: true, color: '#555555'};
  sheet.getRangeByIndexes(5, 0, 1, headers.length).values = [headers];
  sheet.getRangeByIndexes(6, 0, rows.length, headers.length).values = rows;
  const table = sheet.tables.add(`A6:${String.fromCharCode(64 + headers.length)}${n}`, true, name.replace(/ /g, '') + 'Table');
  table.showFilterButton = true;
  const header = sheet.getRangeByIndexes(5, 0, 1, headers.length);
  header.format = {fill: '#9E1B32', font: {name: 'Arial', size: 10, color: '#FFFFFF', bold: true}, rowHeight: 34, wrapText: true, horizontalAlignment: 'center'};
  for (let c = 0; c < widths.length; c++) {
    sheet.getRangeByIndexes(0, c, n, 1).format.columnWidth = widths[c];
  }
  sheet.freezePanes.freezeRows(6);
  return sheet;
}

const typed = (records, columns) => records.map(row => columns.map(col => col === 'date' ? new Date(row[col]) : row[col]));
const train = addTable('Training', 'TTC passenger support: historical training data',
  'Jan-Sep 2025 weekdays. Target: has_recorded_delay. Zero means no matching positive-delay record.',
  fields, typed(data.training, fields), [14, 16, 12, 21, 17, 17, 20, 20, 24]);
train.tabColor = '#9E1B32';
train.getRange(`A7:A${data.training.length + 6}`).setNumberFormat('yyyy-mm-dd');
train.getRange(`F7:I${data.training.length + 6}`).setNumberFormat('0');
train.getRange(`F7:I${data.training.length + 6}`).format.horizontalAlignment = 'right';

const features = fields.slice(0, 5);
const candidates = addTable('Candidates', 'Choose three station-time assignments',
  'Historical exercise: Monday, 6 October 2025. Outcomes withheld.',
  features, typed(data.candidates, features), [16, 18, 16, 25, 24]);
candidates.getRange('A7:A51').setNumberFormat('yyyy-mm-dd');

const guideRows = data.dictionary;
const guide = addTable('Dictionary', 'How to use the data',
  'Only the first five fields are prediction inputs. Other fields are outcomes.',
  ['field', 'role', 'definition'], guideRows, [30, 24, 112]);
guide.getRange('C7:C15').format.wrapText = true;
guide.getRange('A7:C15').format.rowHeight = 30;
guide.getRange('A18').values = [['Read ttc_case/README.md for the cleaning rules, limitations and file guide.']];
guide.getRange('A20').values = [['Passenger volumes, staffing costs and staff effectiveness are not included in this real-data extract.']];
guide.getRange('A22').values = [['Holdout outcomes are stored separately in ttc_case/instructor/.']];

wb.recalculate();
console.log((await wb.inspect({kind: 'table', range: 'Training!A6:I10', include: 'values', tableMaxRows: 5, tableMaxCols: 9})).ndjson);
console.log((await wb.inspect({kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!', options: {useRegex: true, maxResults: 10}})).ndjson);
for (const [sheetName, range] of [['Training', 'A1:I14'], ['Candidates', 'A1:E15'], ['Dictionary', 'A1:C23']]) {
  const image = await wb.render({sheetName, range, scale: 1.5, format: 'png'});
  await fs.writeFile(path.join(previewDir, sheetName.toLowerCase() + '.png'), new Uint8Array(await image.arrayBuffer()));
}
const file = await SpreadsheetFile.exportXlsx(wb);
await file.save(path.join(output, 'ttc_workshop_data.xlsx'));
console.log('Exported ' + path.join(output, 'ttc_workshop_data.xlsx'));
