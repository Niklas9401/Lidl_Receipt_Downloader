#!/usr/bin/env -S deno run --allow-read --allow-write

const harJson = await Deno.readTextFile("receipts.json");
const har = JSON.parse(harJson);

// const resContentJson = har.log.entries[2].response.content.text;
// const resContent = JSON.parse(resContentJson);
// const html = har[0].ticket.htmlPrintedReceipt;

for (let index = 0; index < har.length; index++) {
    const html = har[index].ticket.htmlPrintedReceipt;
    await Deno.writeTextFile(`extracted_receipts/receipt_${index}.html`, html);
}

