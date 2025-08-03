
export const getAccount = async (cliente_id, token) => {
  try {
    const accountsResponse = await fetch(
      `https://baseavanzadag1.onrender.com/clientes/${cliente_id}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "Authorization": `Bearer ${token}`
        }
      }
    );

    if (!accountsResponse.ok) {
      throw new Error("No se pudo obtener las cuentas");
    }

    return await accountsResponse.json();
  } catch (error) {
    console.error("Fallo la obtención de cuentas y tarjetas:", error);
    return [];
  }
};
