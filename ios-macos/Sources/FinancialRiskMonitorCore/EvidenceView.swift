import Charts
import SwiftUI

public struct EvidenceView: View {
    @ObservedObject private var model: AppModel
    @State private var showDiagnostics = false

    public init(model: AppModel) { self.model = model }

    public var body: some View {
        Group {
            if model.featureLoading && model.evidence == nil { ProgressView("Loading model evidence…") }
            else if let error = model.evidenceError, model.evidence == nil { DashboardCard { VStack(alignment: .leading, spacing: 8) { Label("Model evidence unavailable", systemImage: "exclamationmark.triangle.fill").foregroundStyle(DashboardTheme.risk); Text(error).font(.caption).foregroundStyle(.white) } } }
            else if let evidence = model.evidence { content(evidence) }
        }.task { if model.evidence == nil { await model.loadEvidence() } }
    }

    private func content(_ evidence: EvidenceResponse) -> some View {
        ScrollView { VStack(alignment: .leading, spacing: 16) {
            HStack(alignment: .bottom) { VStack(alignment: .leading, spacing: 7) { Text("MODEL EVIDENCE").font(.caption.weight(.bold)).tracking(1.8).foregroundStyle(DashboardTheme.primary); Text("Why should I trust this?").font(.title2.weight(.bold)); Text("Out-of-sample comparison of baseline and GARCH volatility forecasts.").foregroundStyle(DashboardTheme.muted) }; Spacer(); Label("Evidence, not certainty", systemImage: "checkmark.seal.fill").font(.caption).foregroundStyle(DashboardTheme.primary) }
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 170), spacing: 12)], spacing: 12) { info("Evaluation window", "\(date(evidence.evaluationStartDate)) – \(date(evidence.evaluationEndDate))"); info("Sample size", "\(evidence.sampleSize) targets"); info("Baseline window", "\(evidence.baselineWindow) sessions") }
            ViewThatFits(in: .horizontal) { HStack(spacing: 16) { explanation("MAE", "Mean absolute error: the average size of a forecast miss. Lower is better."); explanation("QLIKE", "A variance-forecast loss function that penalizes poor scale estimates. Lower is better.") }; VStack(spacing: 16) { explanation("MAE", "Mean absolute error: the average size of a forecast miss. Lower is better."); explanation("QLIKE", "A variance-forecast loss function that penalizes poor scale estimates. Lower is better.") } }
            charts(evidence)
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 280), spacing: 16)], spacing: 16) { ForEach(["SPY", "QQQ"], id: \.self) { winnerCard(symbol: $0, scores: evidence.scores) } }
            DisclosureGroup("Technical diagnostics: ACF/PACF and scoring notes", isExpanded: $showDiagnostics) { VStack(alignment: .leading, spacing: 10) { Text("Squared-return dependence diagnostics are kept here for technical readers. QLIKE excludes rows with zero or non-positive realized variance.").font(.caption).foregroundStyle(DashboardTheme.muted); Text("Realized proxy: \(evidence.realizedProxy)").font(.caption).foregroundStyle(DashboardTheme.muted) }.padding(.top, 10) }.padding(20).background(DashboardTheme.panel).overlay(RoundedRectangle(cornerRadius: 16).stroke(DashboardTheme.border)).clipShape(RoundedRectangle(cornerRadius: 16))
        }.padding(24) }
    }

    private func info(_ label: String, _ value: String) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 7) { Text(label).font(.caption).foregroundStyle(DashboardTheme.muted); Text(value).font(.subheadline.weight(.bold)) } } }
    private func explanation(_ title: String, _ body: String) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 8) { Text(title).font(.title3.weight(.bold)).foregroundStyle(DashboardTheme.primary); Text(body).font(.caption).foregroundStyle(DashboardTheme.muted).fixedSize(horizontal: false, vertical: true) } }.frame(maxWidth: .infinity) }
    private func charts(_ evidence: EvidenceResponse) -> some View { ViewThatFits(in: .horizontal) { HStack(spacing: 16) { scoreChart("MAE", scores: evidence.scores, value: { $0.mae }); scoreChart("QLIKE", scores: evidence.scores, value: { $0.qlike ?? 0 }) }; VStack(spacing: 16) { scoreChart("MAE", scores: evidence.scores, value: { $0.mae }); scoreChart("QLIKE", scores: evidence.scores, value: { $0.qlike ?? 0 }) } } }
    private func scoreChart(_ title: String, scores: [EvidenceScore], value: @escaping (EvidenceScore) -> Double) -> some View { DashboardCard { VStack(alignment: .leading, spacing: 5) { Text("\(title) by model").font(.headline.weight(.bold)); Text("Lower is better • SPY and QQQ").font(.caption).foregroundStyle(DashboardTheme.muted); Chart(scores.filter { $0.symbol != "ALL" }) { score in BarMark(x: .value("Score", value(score)), y: .value("Model", "\(score.symbol) \(score.model.uppercased())")).foregroundStyle(score.model == "garch" ? DashboardTheme.primary : DashboardTheme.risk) }.frame(height: 150) } }.frame(maxWidth: .infinity) }
    private func winnerCard(symbol: String, scores: [EvidenceScore]) -> some View { let rows = scores.filter { $0.symbol == symbol }; let baseline = rows.first { $0.model == "baseline" }; let garch = rows.first { $0.model == "garch" }; let maeWinner = (garch?.mae ?? .infinity) < (baseline?.mae ?? .infinity) ? "GARCH" : "Baseline"; let qlikeWinner = (garch?.qlike ?? .infinity) < (baseline?.qlike ?? .infinity) ? "GARCH" : "Baseline"; return DashboardCard { VStack(alignment: .leading, spacing: 12) { Text(symbol).font(.caption.weight(.bold)).tracking(1.6).foregroundStyle(DashboardTheme.primary); Text("Model comparison").font(.headline.weight(.bold)); HStack { Text("MAE").foregroundStyle(DashboardTheme.muted); Spacer(); Text("Baseline \(baseline?.mae ?? 0, specifier: "%.3f")"); Text("GARCH \(garch?.mae ?? 0, specifier: "%.3f")").foregroundStyle(DashboardTheme.primary) }; HStack { Text("QLIKE").foregroundStyle(DashboardTheme.muted); Spacer(); Text("Baseline \(baseline?.qlike ?? 0, specifier: "%.3f")"); Text("GARCH \(garch?.qlike ?? 0, specifier: "%.3f")").foregroundStyle(DashboardTheme.primary) }; Text("MAE winner: \(maeWinner) • QLIKE winner: \(qlikeWinner) • \(baseline?.maeRows ?? 0) rows").font(.caption).foregroundStyle(DashboardTheme.muted) } } }
    private func date(_ value: Date) -> String { value.formatted(date: .abbreviated, time: .omitted) }
}
