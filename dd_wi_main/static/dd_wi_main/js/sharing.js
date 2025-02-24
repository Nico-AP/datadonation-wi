function copyLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
    });
}

function shareViaEmail() {
    const subject = encodeURIComponent("Welche politischen Inhalte hast du auf TikTok gesehen?");
    const body = `Welche politischen Inhalte hast du auf TikTok gesehen? Finde es heraus indem du bei dem Projekt mitmachst um eine persönliche Analyse deines Feeds zu erhalten https://dein-feed-deine-wahl.de %0D%0A Ich habe auch mitgemacht und fand's sehr spannend! %0D%0A %0D%0A
Liebe Grüße`;
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
}
