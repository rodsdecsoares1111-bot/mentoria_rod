# MentorIA Social

Painel local para acompanhar publicações do Instagram e LinkedIn, comparar métricas de engajamento e calcular um score de 0 a 100.

## Executar

1. Copie `.env.example` para `.env` e preencha as credenciais das redes.
2. Ative o ambiente virtual e execute `python main.py`.
3. O painel abre em `http://127.0.0.1:8000`.

O Instagram precisa de um token da Graph API e do ID da conta profissional. O LinkedIn precisa de um token com acesso à organização e do ID numérico ou URN da organização. A disponibilidade de impressões e estatísticas de cada publicação depende das permissões aprovadas para o aplicativo em cada plataforma.

O score mantém os pesos existentes: 40% visualizações por dia, 35% interações por visualização e 25% comentários por visualização. Interações incluem curtidas, compartilhamentos, salvamentos e cliques quando a API fornece esses dados. Publicações sem métricas liberadas aparecem com o valor indisponível.
