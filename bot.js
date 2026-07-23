require('dotenv').config();

const { 
  Client, 
  GatewayIntentBits, 
  EmbedBuilder, 
  ActionRowBuilder, 
  ButtonBuilder, 
  ButtonStyle, 
  PermissionsBitField, 
  REST, 
  Routes 
} = require('discord.js');

const TOKEN = process.env.DISCORD_TOKEN;
const CLIENT_ID = process.env.CLIENT_ID;
const GUILD_ID = process.env.GUILD_ID;

// Create the client inline, without naming it 'client'
(new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] }))
  .once('ready', () => {
    console.log('Bot is online!');

    // Register slash commands
    const rest = new REST({ version: '10' }).setToken(TOKEN);
    (async () => {
      try {
        await rest.put(
          Routes.applicationGuildCommands(CLIENT_ID, GUILD_ID),
          { body: [
              { name: 'session', description: 'Create a session embed' },
              { name: 'giveaway', description: 'Create a giveaway embed' }
            ] }
        );
        console.log('Commands registered!');
      } catch (error) {
        console.error('Error registering commands:', error);
      }
    })();
  })
  // Handle commands
  .on('interactionCreate', async interaction => {
    if (!interaction.isChatInputCommand()) return;

    const { commandName } = interaction;

    if (commandName === 'session') {
      if (!interaction.member.permissions.has(PermissionsBitField.Flags.Administrator)) {
        await interaction.reply({ content: 'You do not have permission to use this command.', ephemeral: true });
        return;
      }

      const embed = new EmbedBuilder()
        .setTitle('Los Angeles State Roleplay')
        .setDescription(`Server Name: Los Angeles State RolePlay\n\n**You must be in VC Only**`)
        .addFields(
          { name: 'Host', value: `<@${interaction.user.id}>`, inline: true },
          { name: 'Server Owner', value: 'ova12s\nID: 1435042585583554570', inline: true },
          { name: 'Join Code', value: 'LARPPp', inline: false }
        )
        .setColor(0x00AE86);

      const row = new ActionRowBuilder()
        .addComponents(
          new ButtonBuilder()
            .setLabel('Join Server')
            .setStyle(ButtonStyle.Link)
            .setURL('https://erlc.gg/LARPPp')
        );

      await interaction.reply({ embeds: [embed], components: [row] });
    }

    if (commandName === 'giveaway') {
      const embed = new EmbedBuilder()
        .setTitle('Los Angeles State Roleplay - Giveaway')
        .setDescription('Join the giveaway and win exciting prizes!')
        .setColor(0x00AE86);

      const row = new ActionRowBuilder()
        .addComponents(
          new ButtonBuilder()
            .setLabel('Join Server')
            .setStyle(ButtonStyle.Link)
            .setURL('https://erlc.gg/LARPPp')
        );

      await interaction.reply({ embeds: [embed], components: [row] });
    }
  })
  // Log in the bot
  .login(TOKEN);
