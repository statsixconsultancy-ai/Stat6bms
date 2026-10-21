import React from 'react';

interface GeminiMarkdownRendererProps {
  content: string;
  className?: string;
}

export const GeminiMarkdownRenderer: React.FC<GeminiMarkdownRendererProps> = ({ content, className = '' }) => {
  if (!content) return null;

  // Helper to render inline formatting: bold, italic, code
  const renderInline = (text: string): React.ReactNode => {
    // Split by code, bold, italic
    const parts: React.ReactNode[] = [];
    let remaining = text;
    let keyIdx = 0;

    // Regex for **bold**, `code`, *italic*
    const inlineRegex = /(\*\*([^*]+)\*\*|`([^`]+)`|\*([^*]+)\*)/;

    while (remaining) {
      const match = remaining.match(inlineRegex);
      if (!match) {
        parts.push(remaining);
        break;
      }

      const matchIndex = match.index ?? 0;
      if (matchIndex > 0) {
        parts.push(remaining.slice(0, matchIndex));
      }

      const fullMatch = match[0];
      if (fullMatch.startsWith('**') && fullMatch.endsWith('**')) {
        parts.push(
          <strong key={keyIdx++} className="font-semibold text-white">
            {match[2]}
          </strong>
        );
      } else if (fullMatch.startsWith('`') && fullMatch.endsWith('`')) {
        parts.push(
          <code
            key={keyIdx++}
            className="px-1.5 py-0.5 rounded-md bg-slate-800 text-blue-300 font-mono text-[11px] border border-slate-700/60"
          >
            {match[3]}
          </code>
        );
      } else if (fullMatch.startsWith('*') && fullMatch.endsWith('*')) {
        parts.push(
          <em key={keyIdx++} className="italic text-slate-300">
            {match[4]}
          </em>
        );
      }

      remaining = remaining.slice(matchIndex + fullMatch.length);
    }

    return parts;
  };

  // Helper to parse markdown table lines
  const parseTable = (lines: string[]): { headers: string[]; rows: string[][] } | null => {
    if (lines.length < 2) return null;
    
    // First line is headers
    const rawHeaders = lines[0]
      .split('|')
      .map(c => c.trim())
      .filter((c, i, arr) => i > 0 && i < arr.length - 1 || c !== '');
    
    // Second line must be separator (---|---|---)
    const isSeparator = lines[1].includes('-') && lines[1].includes('|');
    if (!isSeparator) return null;

    const rows: string[][] = [];
    for (let i = 2; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line || !line.includes('|')) continue;
      const cells = line
        .split('|')
        .map(c => c.trim())
        .filter((c, cellIdx, arr) => cellIdx > 0 && cellIdx < arr.length - 1 || c !== '');
      if (cells.length > 0) {
        rows.push(cells);
      }
    }

    return { headers: rawHeaders, rows };
  };

  // Split lines into structured blocks (Headings, Tables, Lists, Paragraphs)
  const lines = content.split('\n');
  const blocks: React.ReactNode[] = [];
  let i = 0;
  let blockKey = 0;

  while (i < lines.length) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    // 1. Skip empty lines
    if (!trimmed) {
      i++;
      continue;
    }

    // 2. Check for Markdown Table (starts with |)
    if (trimmed.startsWith('|') && trimmed.includes('|') && i + 1 < lines.length && lines[i + 1].includes('|') && lines[i + 1].includes('-')) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        tableLines.push(lines[i].trim());
        i++;
      }

      const tableData = parseTable(tableLines);
      if (tableData && tableData.headers.length > 0) {
        blocks.push(
          <div key={`table-${blockKey++}`} className="my-3 overflow-hidden rounded-xl border border-slate-700/70 bg-[#12192b]/90 shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-[#1b253b] text-slate-200 border-b border-slate-700/80">
                  <tr>
                    {tableData.headers.map((hdr, hIdx) => {
                      const isRight = hIdx > 0 && /value|amount|price|revenue|cost|margin|%/i.test(hdr);
                      return (
                        <th
                          key={hIdx}
                          className={`px-3.5 py-2.5 font-semibold text-[11px] tracking-wider uppercase text-slate-300 ${
                            isRight ? 'text-right' : 'text-left'
                          }`}
                        >
                          {hdr}
                        </th>
                      );
                    })}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80">
                  {tableData.rows.map((row, rIdx) => (
                    <tr
                      key={rIdx}
                      className="hover:bg-slate-800/40 transition-colors duration-150 odd:bg-transparent even:bg-slate-900/20"
                    >
                      {row.map((cell, cIdx) => {
                        const isNumericOrCurrency = /^\$|%|\d/.test(cell.trim()) || (cIdx > 0 && tableData.headers[cIdx] && /value|amount|price|revenue|cost|margin|%/i.test(tableData.headers[cIdx]));
                        return (
                          <td
                            key={cIdx}
                            className={`px-3.5 py-2 text-slate-200 text-xs ${
                              isNumericOrCurrency ? 'text-right font-mono text-slate-100' : 'text-left font-normal'
                            }`}
                          >
                            {renderInline(cell)}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
        continue;
      }
    }

    // 3. Headings
    if (trimmed.startsWith('### ')) {
      blocks.push(
        <h3 key={`h3-${blockKey++}`} className="text-[14px] font-bold text-white tracking-tight mt-3 mb-1.5 flex items-center gap-2">
          <span className="w-1.5 h-3.5 rounded-full bg-gradient-to-b from-blue-400 to-indigo-500"></span>
          <span>{trimmed.replace('### ', '')}</span>
        </h3>
      );
      i++;
      continue;
    }
    if (trimmed.startsWith('## ')) {
      blocks.push(
        <h2 key={`h2-${blockKey++}`} className="text-[15px] font-bold text-white tracking-tight mt-4 mb-2">
          {trimmed.replace('## ', '')}
        </h2>
      );
      i++;
      continue;
    }
    if (trimmed.startsWith('# ')) {
      blocks.push(
        <h1 key={`h1-${blockKey++}`} className="text-[16px] font-bold text-white tracking-tight mt-4 mb-2">
          {trimmed.replace('# ', '')}
        </h1>
      );
      i++;
      continue;
    }

    // 4. Bullet lists (- or * followed by space)
    if (/^[-*]\s+/.test(trimmed)) {
      const listItems: string[] = [];
      while (i < lines.length && /^[-*]\s+/.test(lines[i].trim())) {
        listItems.push(lines[i].trim().replace(/^[-*]\s+/, ''));
        i++;
      }
      blocks.push(
        <ul key={`list-${blockKey++}`} className="space-y-1.5 my-2 pl-1">
          {listItems.map((item, lIdx) => (
            <li key={lIdx} className="flex items-start gap-2.5 text-xs text-slate-200 leading-relaxed">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 flex-shrink-0 shadow-xs"></span>
              <div className="flex-1">{renderInline(item)}</div>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // 5. Regular paragraph
    blocks.push(
      <p key={`p-${blockKey++}`} className="text-xs text-slate-200 leading-relaxed my-1.5">
        {renderInline(trimmed)}
      </p>
    );
    i++;
  }

  return <div className={`gemini-markdown-container space-y-1 ${className}`}>{blocks}</div>;
};
