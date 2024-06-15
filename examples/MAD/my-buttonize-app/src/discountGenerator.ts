export const handler = async (event: { discountValue: number }) => {
	console.log(`Generating discount of value ${event.discountValue}`)

	return {
		discountValue: event.discountValue,
		code: `${Math.random()}`.split('.')[1]
	}
}
