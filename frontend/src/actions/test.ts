'use server';

export async function testServerAction() {
  console.log('Server action executed');
  return { success: true, message: 'Server action working!' };
}