export function getFormatters() {
  const defaultLocale = "de-CH"; // chosen for delimiters (thousands and decimal)

  const getCurrencySymbol = (currency = "CHF") => {
    const formatter = new Intl.NumberFormat("en-US", {
      // "en-US" to get reliable symbol output
      style: "currency",
      currency: currency,
      currencyDisplay: "narrowSymbol",
    });

    const parts = formatter.formatToParts(0);
    const symbolPart = parts.find((part) => part.type === "currency");

    return symbolPart ? symbolPart.value : currency;
  };

  const getCurrencyPrefix = (currency) => {
    return `${getCurrencySymbol(currency)}\u202F`;
  };

  const formatCurrency = (value, currency) => {
    if (value == null || isNaN(value)) return "—";

    const formatter = new Intl.NumberFormat(defaultLocale, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });

    return `${getCurrencyPrefix(currency)}${formatter.format(value)}`;
  };

  const monoSpaceCurrency = (value, currency) => {
    if (value == null || isNaN(value)) return "—";

    const formatter = new Intl.NumberFormat(defaultLocale, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });

    return `<span class="font-mono">${getCurrencySymbol(currency)}</span>\u202F<span class="font-mono">${formatter.format(value)}</span>`;
  };

  const formatDate = (value) => {
    if (!value) return "";

    return new Intl.DateTimeFormat("en-CH", {
      // "en" instead of defaultLocale for English month names
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(value));
  };

  return {
    getCurrencyPrefix,
    formatCurrency,
    monoSpaceCurrency,
    formatDate,
    defaultLocale,
  };
}
