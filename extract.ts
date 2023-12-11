#!/usr/bin/env -S deno run --allow-read --allow-write

const json = await Deno.readTextFile("receipts.json");
const parsed_json = JSON.parse(json);

for (let index = 0; index < parsed_json.length; index++) {
    const html = parsed_json[index].ticket.htmlPrintedReceipt;
    await Deno.writeTextFile(`extracted_receipts/receipt_${index}.html`, html);
}

