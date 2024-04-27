function delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
    console.log("Start");
    await delay(1000);
    console.log("Middle");
    await delay(1000);
    console.log("End");
}

main();