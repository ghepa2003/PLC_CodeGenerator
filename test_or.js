const test = async () => {
  const response = await fetch('https://openrouter.io/api/v1/auth/key', {
    method: 'GET',
    headers: {
      'Authorization': 'Bearer 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'
    }
  });
  console.log(response.status, response.statusText);
  const text = await response.text();
  console.log(text);
};
test();
