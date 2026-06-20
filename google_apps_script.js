// ============================================================
// PlayerReportManager — Google Apps Script Backend
// Crystalfbft | by saransh-ops
// Deploy as Web App: Execute as Me, Anyone can access
// ============================================================

const SHEET_NAME = "Reports";
const DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1517479910267027576/kGyVz3P2CAUmMuU0aMgs__sYozRgK95-4pfw8HQi7p4P_nSS9AJGZ627an8aatavI6P8"; // REQUIRED — get from Discord channel settings > Integrations > Webhooks

function generateReportId() {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let id = "RPT-";
  for (let i = 0; i < 6; i++) id += chars[Math.floor(Math.random() * chars.length)];
  return id;
}

const SPREADSHEET_ID = "1dr-BiEOH5jBDkJPYAmqgCJH7d7YrXavE-TKm0RFxwpA"; // paste the ID from your sheet URL

function getSheet() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow([
      "Report ID", "Timestamp", "Reporter", "Accused",
      "Reason", "Description", "Evidence", "Status",
      "Staff Notes", "Resolved By", "Last Updated"
    ]);
    sheet.setFrozenRows(1);
    // Style header
    sheet.getRange(1, 1, 1, 11).setBackground("#1a1a2e").setFontColor("#00f5d4").setFontWeight("bold");
  }
  return sheet;
}

function doPost(e) {
  const params = e.parameter;
  const action = params.action || "submit_report";

  try {
    if (action === "submit_report") return submitReport(params);
    if (action === "update_status") return updateStatus(params);
    if (action === "add_note") return addNote(params);
    if (action === "user_reply") return userReply(params);
    return jsonResponse({ result: "error", message: "Unknown action" });
  } catch (err) {
    return jsonResponse({ result: "error", message: err.toString() });
  }
}

function doGet(e) {
  const params = e.parameter;
  const action = params.action || "get_report";

  try {
    if (action === "get_report") return getReport(params);
    if (action === "list_reports") return listReports(params);
    return jsonResponse({ result: "error", message: "Unknown action" });
  } catch (err) {
    return jsonResponse({ result: "error", message: err.toString() });
  }
}

function submitReport(params) {
  Logger.log("submitReport called with: " + JSON.stringify(params));
  const sheet = getSheet();
  Logger.log("Sheet obtained: " + sheet.getName());
  const reportId = generateReportId();
  const timestamp = new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });

  // Duplicate check — same reporter + accused in last 24hrs
  const data = sheet.getDataRange().getValues();
  const now = new Date();
  for (let i = 1; i < data.length; i++) {
    const rowTime = new Date(data[i][1]);
    const hoursDiff = (now - rowTime) / 36e5;
    if (
      data[i][2].toLowerCase() === (params.reporter || "").toLowerCase() &&
      data[i][3].toLowerCase() === (params.accused || "").toLowerCase() &&
      hoursDiff < 24
    ) {
      Logger.log("Duplicate report blocked");
      return jsonResponse({ result: "error", message: "You already reported this player recently. Please wait 24 hours." });
    }
  }

  sheet.appendRow([
    reportId,
    timestamp,
    params.reporter || "Anonymous",
    params.accused || "Unknown",
    params.reason || "Other",
    params.description || "",
    params.evidence || "",
    "Open",
    "",
    "",
    timestamp
  ]);
  Logger.log("Row appended: " + reportId);

  // Color row by priority
  const lastRow = sheet.getLastRow();
  const highPriority = ["Hacking", "Bug Abuse"].includes(params.reason);
  const medPriority = ["Griefing", "Harassment"].includes(params.reason);
  const color = highPriority ? "#3b0a0a" : medPriority ? "#2d2200" : "#0a1a0a";
  sheet.getRange(lastRow, 1, 1, 11).setBackground(color);
  Logger.log("Row colored");

  const report = {
    reportId, timestamp,
    reporter: params.reporter,
    accused: params.accused,
    reason: params.reason,
    description: params.description,
    evidence: params.evidence
  };

  Logger.log("About to call sendDiscordAlert");
  sendDiscordAlert(report);
  Logger.log("sendDiscordAlert call finished");
  return jsonResponse({ result: "success", reportId });
}

function getReport(params) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();
  const id = (params.reportId || "").trim().toUpperCase();

  for (let i = 1; i < data.length; i++) {
    if (data[i][0].toString().toUpperCase() === id) {
      return jsonResponse({
        result: "success",
        reportId: data[i][0],
        timestamp: data[i][1],
        reporter: data[i][2],
        accused: data[i][3],
        reason: data[i][4],
        description: data[i][5],
        evidence: data[i][6],
        status: data[i][7],
        staffNotes: data[i][8],
        resolvedBy: data[i][9],
        lastUpdated: data[i][10]
      });
    }
  }
  return jsonResponse({ result: "error", message: "Report not found." });
}

function listReports(params) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();
  const filterStatus = params.status || null;
  const filterAccused = params.accused ? params.accused.toLowerCase() : null;
  const reports = [];

  for (let i = 1; i < data.length; i++) {
    if (filterStatus && data[i][7] !== filterStatus) continue;
    if (filterAccused && !data[i][3].toLowerCase().includes(filterAccused)) continue;
    reports.push({
      reportId: data[i][0],
      timestamp: data[i][1],
      reporter: data[i][2],
      accused: data[i][3],
      reason: data[i][4],
      description: data[i][5].toString().substring(0, 100),
      evidence: data[i][6],
      status: data[i][7],
      staffNotes: data[i][8],
      resolvedBy: data[i][9]
    });
  }

  // Sort: Open first, then by date desc
  reports.sort((a, b) => {
    if (a.status === "Open" && b.status !== "Open") return -1;
    if (b.status === "Open" && a.status !== "Open") return 1;
    return new Date(b.timestamp) - new Date(a.timestamp);
  });

  return jsonResponse({ result: "success", reports, total: reports.length });
}

function updateStatus(params) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();
  const id = (params.reportId || "").trim().toUpperCase();

  for (let i = 1; i < data.length; i++) {
    if (data[i][0].toString().toUpperCase() === id) {
      const timestamp = new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
      sheet.getRange(i + 1, 8).setValue(params.status);
      sheet.getRange(i + 1, 10).setValue(params.resolvedBy || "Staff");
      sheet.getRange(i + 1, 11).setValue(timestamp);
      // Update row color for resolved/rejected
      if (params.status === "Resolved") sheet.getRange(i+1,1,1,11).setBackground("#0a1f0a");
      if (params.status === "Rejected") sheet.getRange(i+1,1,1,11).setBackground("#1f0a0a");
      if (params.status === "Investigating") sheet.getRange(i+1,1,1,11).setBackground("#0a0a1f");
      return jsonResponse({ result: "success" });
    }
  }
  return jsonResponse({ result: "error", message: "Report not found." });
}

function addNote(params) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();
  const id = (params.reportId || "").trim().toUpperCase();

  for (let i = 1; i < data.length; i++) {
    if (data[i][0].toString().toUpperCase() === id) {
      const timestamp = new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
      const existing = data[i][8] ? data[i][8] + "\n" : "";
      const newNote = `[${timestamp}] [${params.staffName || "Staff"}]: ${params.note}`;
      sheet.getRange(i + 1, 9).setValue(existing + newNote);
      sheet.getRange(i + 1, 11).setValue(timestamp);
      return jsonResponse({ result: "success" });
    }
  }
  return jsonResponse({ result: "error", message: "Report not found." });
}

function userReply(params) {
  // Players can add follow-up info to their own report
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();
  const id = (params.reportId || "").trim().toUpperCase();

  for (let i = 1; i < data.length; i++) {
    if (data[i][0].toString().toUpperCase() === id) {
      const timestamp = new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
      const existing = data[i][8] ? data[i][8] + "\n" : "";
      const newNote = `[${timestamp}] [Player]: ${params.message}`;
      sheet.getRange(i + 1, 9).setValue(existing + newNote);
      sheet.getRange(i + 1, 11).setValue(timestamp);
      return jsonResponse({ result: "success" });
    }
  }
  return jsonResponse({ result: "error", message: "Report not found." });
}

function testWebhook() {
  sendDiscordAlert({
    reportId: "RPT-TEST01",
    timestamp: new Date().toString(),
    reporter: "TestUser",
    accused: "TestAccused",
    reason: "Other",
    description: "This is a manual test from the Apps Script editor."
  });
}

function sendDiscordAlert(report) {
  Logger.log("sendDiscordAlert entered");

  try {
    const webhook = DISCORD_WEBHOOK;

    if (!webhook) {
      Logger.log("Webhook URL missing");
      return;
    }

    const priority =
      ["Hacking", "Bug Abuse"].includes(report.reason)
        ? "🔴 HIGH"
        : ["Griefing", "Harassment"].includes(report.reason)
        ? "🟡 MEDIUM"
        : "🟢 LOW";

    const color =
      priority.includes("HIGH")
        ? 16711680
        : priority.includes("MEDIUM")
        ? 16753920
        : 65280;

    const payload = {
      embeds: [
        {
          title: "🚨 New Player Report",
          color: color,

          thumbnail: {
            url: "https://mc-heads.net/avatar/" + encodeURIComponent(report.accused || "Steve")
          },

          fields: [
            {
              name: "📋 Report ID",
              value: String(report.reportId || "Unknown"),
              inline: true
            },
            {
              name: "⚠️ Priority",
              value: priority,
              inline: true
            },
            {
              name: "👤 Reporter",
              value: String(report.reporter || "Anonymous"),
              inline: true
            },
            {
              name: "🎯 Accused",
              value: String(report.accused || "Unknown"),
              inline: true
            },
            {
              name: "📝 Reason",
              value: String(report.reason || "Other"),
              inline: true
            },
            {
              name: "📄 Description",
              value: String(report.description || "No description").substring(0, 1000)
            }
          ],

          footer: {
            text: "Crystalfbft Report System"
          },

          timestamp: new Date().toISOString()
        }
      ]
    };

    if (report.evidence) {
      payload.embeds[0].fields.push({
        name: "🔗 Evidence",
        value: String(report.evidence).substring(0, 1000)
      });
    }

    Logger.log("Payload: " + JSON.stringify(payload));

    const response = UrlFetchApp.fetch(webhook, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });

    Logger.log("Discord code: " + response.getResponseCode());
    Logger.log("Discord body: " + response.getContentText());

  } catch (e) {
    Logger.log("Discord exception: " + e);
    Logger.log("Discord stack: " + e.stack);
  }
}

function testWebhookOnly() {
  const response = UrlFetchApp.fetch(DISCORD_WEBHOOK, {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({
      content: "Webhook test at " + new Date()
    }),
    muteHttpExceptions: true
  });

  Logger.log(response.getResponseCode());
  Logger.log(response.getContentText());
}

function jsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

function doOptions(e) {
  return ContentService.createTextOutput("")
    .setMimeType(ContentService.MimeType.TEXT);
}