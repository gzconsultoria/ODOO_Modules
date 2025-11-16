/** @odoo-module **/

/**
 * Calculadora FIRE - Financial Independence, Retire Early
 * Módulo Odoo 19 - Client-side Calculator
 * Autor: Geovane Zomer - GZ Consultoria
 */

(function () {
    'use strict';

    // Aguarda carregamento completo do DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFireCalculator);
    } else {
        initFireCalculator();
    }

    function initFireCalculator() {
        console.log('🔥 Inicializando Calculadora FIRE...');

        // ===================== CONSTANTES =====================
        const STORAGE_KEY = 'fireCalculatorSettings_odoo';
        let recalcTimer = null;

        // ===================== FUNÇÕES AUXILIARES =====================

        function readNum(container, selector, fallback) {
            const el = container.querySelector(selector);
            if (!el) return fallback;
            const v = parseFloat(String(el.value).replace(',', '.'));
            return isNaN(v) ? fallback : v;
        }

        function readPct(container, selector, fallback) {
            if (selector === '#withdrawalRateRange' || 
                selector === '#expenseIncreaseRange' || 
                selector === '#investmentRange') {
                const el = container.querySelector(selector);
                if (!el) return fallback;
                const v = parseFloat(el.value);
                return isNaN(v) ? fallback : v / 100;
            }
            return readNum(container, selector, fallback * 100) / 100;
        }

        function isValidNumber(value, fieldName) {
            if (typeof value !== 'number' || isNaN(value)) {
                console.error(`Valor inválido para ${fieldName}: não é um número`);
                return false;
            }
            if (!isFinite(value)) {
                console.error(`Valor inválido para ${fieldName}: não é finito (${value})`);
                return false;
            }
            return true;
        }

        function fmtBR(n) {
            if (!isValidNumber(n, 'formatação')) return 'R$ 0,00';
            return new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(n);
        }

        function fmtPercent(n) {
            if (!isValidNumber(n, 'formatação percentual')) return '0%';
            return n.toFixed(1) + '%';
        }

        function safePower(base, exponent) {
            return Math.pow(1 + base, exponent);
        }

        function showError(container, msg) {
            console.error('Erro na calculadora FIRE:', msg);
            const existingAlert = container.querySelector('.alert.alert-danger');
            if (existingAlert) existingAlert.remove();
            
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger mb-3';
            alert.innerHTML = `<h6>Erro</h6><p>${msg}</p>`;
            container.querySelector('.fire-calculator-content').prepend(alert);
        }

        function saveSettings(container) {
            try {
                const settings = {
                    realMode: container.querySelector('#realMode').checked,
                    currentAge: container.querySelector('#currentAge').value,
                    retirementAge: container.querySelector('#retirementAge').value,
                    monthlyExpenses: container.querySelector('#monthlyExpenses').value,
                    monthlyIncome: container.querySelector('#monthlyIncome').value,
                    currentInvestments: container.querySelector('#currentInvestments').value,
                    monthlySavings: container.querySelector('#monthlySavings').value,
                    investmentRange: container.querySelector('#investmentRange').value,
                    expenseIncreaseRange: container.querySelector('#expenseIncreaseRange').value,
                    withdrawalRateRange: container.querySelector('#withdrawalRateRange').value,
                    expectedReturn: container.querySelector('#expectedReturn').value,
                    inflationRate: container.querySelector('#inflationRate').value
                };
                localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
            } catch (e) {
                console.error('Erro ao salvar configurações:', e);
            }
        }

        function loadSettings(container) {
            try {
                const saved = localStorage.getItem(STORAGE_KEY);
                if (saved) {
                    const settings = JSON.parse(saved);
                    container.querySelector('#realMode').checked = settings.realMode;
                    container.querySelector('#currentAge').value = settings.currentAge;
                    container.querySelector('#retirementAge').value = settings.retirementAge;
                    container.querySelector('#monthlyExpenses').value = settings.monthlyExpenses;
                    container.querySelector('#monthlyIncome').value = settings.monthlyIncome;
                    container.querySelector('#currentInvestments').value = settings.currentInvestments;
                    container.querySelector('#monthlySavings').value = settings.monthlySavings;
                    container.querySelector('#investmentRange').value = settings.investmentRange;
                    container.querySelector('#expenseIncreaseRange').value = settings.expenseIncreaseRange;
                    container.querySelector('#withdrawalRateRange').value = settings.withdrawalRateRange;
                    container.querySelector('#expectedReturn').value = settings.expectedReturn;
                    container.querySelector('#inflationRate').value = settings.inflationRate;

                    container.querySelector('#investmentValue').textContent = settings.investmentRange + '%';
                    container.querySelector('#expenseIncreaseValue').textContent = settings.expenseIncreaseRange + '%';
                    container.querySelector('#withdrawalRateValue').textContent = settings.withdrawalRateRange + '%';

                    const label = container.querySelector('#realModeLabel');
                    label.textContent = settings.realMode ? 
                        'Considerar efeito da inflação nos cálculos' : 
                        'Inflação = 0% (valores nominais)';
                    return true;
                }
            } catch (e) {
                console.error('Erro ao carregar configurações:', e);
            }
            return false;
        }

        function calculateFutureValue(pv, rate, nper, pmt = 0) {
            if (rate === 0) return pv + (pmt * nper);
            const monthlyRate = rate / 12;
            const factor = safePower(monthlyRate, nper);
            return pv * factor + pmt * ((factor - 1) / monthlyRate);
        }

        function calculatePeriods(pv, fv, pmt, rate) {
            if (pv >= fv) return 0;
            if (rate === 0) return pmt > 0 ? (fv - pv) / pmt : Infinity;
            const monthlyRate = rate / 12;
            if (pmt === 0) {
                return pv > 0 ? Math.log(fv / pv) / Math.log(1 + monthlyRate) : Infinity;
            }
            const numerator = Math.log((fv * monthlyRate + pmt) / (pv * monthlyRate + pmt));
            const denominator = Math.log(1 + monthlyRate);
            return Math.max(0, numerator / denominator);
        }

        function formatPeriod(months) {
            if (!isFinite(months) || months < 0) return 'Indeterminado';
            if (months === 0) return 'Meta atingida!';
            const years = Math.floor(months / 12);
            const remainingMonths = Math.round(months % 12);
            
            if (years === 0) return `${remainingMonths} mes${remainingMonths !== 1 ? 'es' : ''}`;
            if (remainingMonths === 0) return `${years} ano${years !== 1 ? 's' : ''}`;
            return `${years} ano${years !== 1 ? 's' : ''} e ${remainingMonths} mes${remainingMonths !== 1 ? 'es' : ''}`;
        }

        function scheduleRecalc(container) {
            clearTimeout(recalcTimer);
            recalcTimer = setTimeout(() => recalc(container), 100);
        }

        // ===================== CÁLCULO PRINCIPAL =====================

        function recalc(container) {
            try {
                const realMode = container.querySelector('#realMode').checked;
                const currentAge = Math.max(18, Math.floor(readNum(container, '#currentAge', 30)));
                const retirementAge = Math.max(30, Math.floor(readNum(container, '#retirementAge', 55)));
                const monthlyExpenses = Math.max(0, readNum(container, '#monthlyExpenses', 5000));
                const monthlyIncome = Math.max(0, readNum(container, '#monthlyIncome', 8000));
                const currentInvestments = Math.max(0, readNum(container, '#currentInvestments', 100000));
                const monthlySavings = Math.max(0, readNum(container, '#monthlySavings', 2000));
                
                const investmentCoverage = readPct(container, '#investmentRange', 0.2);
                const expenseInflation = readPct(container, '#expenseIncreaseRange', 0);
                const annualReturn = readPct(container, '#expectedReturn', 0.12);
                const annualInflation = readPct(container, '#inflationRate', 0.04);
                const safeWithdrawalRate = Math.max(0.001, readPct(container, '#withdrawalRateRange', 0.04));
                
                const yearsToRetirement = retirementAge - currentAge;
                const monthsToRetirement = yearsToRetirement * 12;

                if (yearsToRetirement <= 0) {
                    showError(container, 'A idade de aposentadoria deve ser maior que a idade atual.');
                    return;
                }
                if (monthlyExpenses <= 0) {
                    showError(container, 'Os gastos mensais devem ser positivos.');
                    return;
                }

                container.querySelectorAll('.alert.alert-danger').forEach(el => el.remove());

                const realReturn = realMode ? (annualReturn - annualInflation) : annualReturn;
                const futureMonthlyExpenses = monthlyExpenses * (1 + expenseInflation);
                const futureAnnualExpenses = futureMonthlyExpenses * 12;

                // FIRE Tradicional
                const traditionalFireTarget = futureAnnualExpenses / safeWithdrawalRate;
                const traditionalProgress = Math.min((currentInvestments / traditionalFireTarget) * 100, 100);
                
                let traditionalMonthsToGoal = Infinity;
                if (monthlySavings > 0 && currentInvestments < traditionalFireTarget) {
                    traditionalMonthsToGoal = calculatePeriods(currentInvestments, traditionalFireTarget, monthlySavings, realReturn);
                }

                // Coast FIRE
                const coastFireRequired = traditionalFireTarget / Math.pow(1 + realReturn / 12, monthsToRetirement);
                const coastFireProgress = Math.min((currentInvestments / coastFireRequired) * 100, 100);
                const coastFireGrowth = calculateFutureValue(coastFireRequired, realReturn, monthsToRetirement);
                
                let coastFireMonthsToGoal = Infinity;
                if (monthlySavings > 0 && currentInvestments < coastFireRequired) {
                    coastFireMonthsToGoal = calculatePeriods(currentInvestments, coastFireRequired, monthlySavings, realReturn);
                }

                // Barista FIRE
                const baristaFireTarget = (futureAnnualExpenses * investmentCoverage) / safeWithdrawalRate;
                const baristaProgress = Math.min((currentInvestments / baristaFireTarget) * 100, 100);
                const baristaPartTimeIncome = futureMonthlyExpenses * (1 - investmentCoverage);
                
                let baristaMonthsToGoal = Infinity;
                if (monthlySavings > 0 && currentInvestments < baristaFireTarget) {
                    baristaMonthsToGoal = calculatePeriods(currentInvestments, baristaFireTarget, monthlySavings, realReturn);
                }

                // Análises
                const currentRunway = currentInvestments / monthlyExpenses;
                const savingsRate = monthlyIncome > 0 ? (monthlySavings / monthlyIncome) * 100 : 0;
                const projectedWealth = calculateFutureValue(currentInvestments, realReturn, monthsToRetirement, monthlySavings);
                const currentMonthlyIncome = (currentInvestments * safeWithdrawalRate) / 12;
                const expensesCovered = monthlyExpenses > 0 ? (currentMonthlyIncome / monthlyExpenses) * 100 : 0;

                if (!isValidNumber(traditionalFireTarget, 'FIRE tradicional') || 
                    !isValidNumber(coastFireRequired, 'Coast FIRE') || 
                    !isValidNumber(baristaFireTarget, 'Barista FIRE')) {
                    showError(container, 'Erro nos cálculos. Verifique os valores inseridos.');
                    return;
                }

                // ===================== ATUALIZAÇÃO DA INTERFACE =====================

                // Resumo
                container.querySelector('#expensesCovered').textContent = fmtPercent(expensesCovered);
                container.querySelector('#currentRunway').textContent = formatPeriod(currentRunway);
                container.querySelector('#savingsRate').textContent = fmtPercent(savingsRate);

                // Milestones
                const milestones = [
                    { value: 250000, iconId: '#milestone250kIcon', statusId: '#milestone250kStatus' },
                    { value: 500000, iconId: '#milestone500kIcon', statusId: '#milestone500kStatus' },
                    { value: 1000000, iconId: '#milestone1MIcon', statusId: '#milestone1MStatus' }
                ];

                milestones.forEach(milestone => {
                    const icon = container.querySelector(milestone.iconId);
                    const status = container.querySelector(milestone.statusId);
                    
                    if (currentInvestments >= milestone.value) {
                        icon.textContent = '🏆';
                        icon.style.filter = 'grayscale(0)';
                        icon.style.transform = 'scale(1.1)';
                        status.innerHTML = '<strong style="color: #4caf50;">✓ Conquistado!</strong>';
                    } else {
                        const monthsToMilestone = calculatePeriods(currentInvestments, milestone.value, monthlySavings, realReturn);
                        icon.textContent = '🔒';
                        icon.style.filter = 'grayscale(0.7)';
                        icon.style.opacity = '0.5';
                        
                        if (isFinite(monthsToMilestone) && monthsToMilestone > 0) {
                            status.innerHTML = `Faltam <strong>${formatPeriod(monthsToMilestone)}</strong>`;
                        } else {
                            status.textContent = 'Aumente seus aportes';
                        }
                    }
                });

                // Avisos inteligentes
                let warnings = [];
                
                if (savingsRate > 0 && savingsRate < 20) {
                    warnings.push({
                        icon: 'fa-piggy-bank',
                        color: '#ff9800',
                        text: `Sua taxa de poupança está em ${fmtPercent(savingsRate)}. Considere aumentá-la para pelo menos 20% para acelerar sua jornada FIRE.`
                    });
                }
                
                const realReturnPercent = realReturn * 100;
                if (realMode && realReturnPercent < 6) {
                    warnings.push({
                        icon: 'fa-chart-line',
                        color: '#ff9800',
                        text: `Com inflação de ${fmtPercent(annualInflation * 100)}, seu retorno real é apenas ${fmtPercent(realReturnPercent)}. Verifique se suas expectativas estão alinhadas com seu perfil de investimentos.`
                    });
                }
                
                const swrPercent = safeWithdrawalRate * 100;
                if (swrPercent > 4.5) {
                    warnings.push({
                        icon: 'fa-triangle-exclamation',
                        color: '#f44336',
                        text: `Taxa de retirada (SWR) de ${fmtPercent(swrPercent)} pode ser arriscado. A regra clássica recomenda 4% ao ano ou menos.`
                    });
                }
                
                const warningsContainer = container.querySelector('#smartWarnings');
                if (warnings.length > 0) {
                    warningsContainer.innerHTML = warnings.map(w => 
                        `<div class="alert alert-warning mb-2 d-flex align-items-start">
                            <i class="fa-solid ${w.icon} me-2 mt-1" style="color: ${w.color};"></i>
                            <span style="font-size: 13px;">${w.text}</span>
                        </div>`
                    ).join('');
                    warningsContainer.style.display = 'block';
                } else {
                    warningsContainer.style.display = 'none';
                }

                // FIRE Tradicional
                container.querySelector('#fireProgressPercent').textContent = traditionalProgress.toFixed(1) + '%';
                container.querySelector('#fireProgressBar').style.width = Math.min(traditionalProgress, 100) + '%';
                container.querySelector('#fireCurrentAmount').textContent = fmtBR(currentInvestments);
                container.querySelector('#fireTargetAmount').textContent = fmtBR(traditionalFireTarget);

                const faltaValor = traditionalFireTarget - currentInvestments;
                const statusAlert = container.querySelector('#statusAlert');
                const currentStatus = container.querySelector('#currentStatus');
                
                if (traditionalProgress >= 100) {
                    statusAlert.className = 'alert alert-success';
                    currentStatus.innerHTML = `🎉 Parabéns! Você já atingiu sua meta, considerando a taxa de retirada segura de <strong>${(safeWithdrawalRate * 100).toFixed(1)}%</strong> (SWR).`;
                } else {
                    statusAlert.className = 'alert alert-warning';
                    currentStatus.innerHTML = `Faltam ${fmtBR(faltaValor)} para atingir sua meta, considerando a taxa de retirada segura de <strong>${(safeWithdrawalRate * 100).toFixed(1)}%</strong> (SWR). Continue firme!`;
                }

                // Barista FIRE
                container.querySelector('#baristaProgress').textContent = baristaProgress.toFixed(1) + '%';
                container.querySelector('#baristaProgressBar').style.width = Math.min(baristaProgress, 100) + '%';
                container.querySelector('#baristaTarget').textContent = fmtBR(baristaFireTarget);
                container.querySelector('#baristaPartTime').textContent = fmtBR(baristaPartTimeIncome);
                
                const baristaPeriod = container.querySelector('#baristaPeriod');
                if (isFinite(baristaMonthsToGoal) && baristaMonthsToGoal > 0) {
                    baristaPeriod.innerHTML = `Em <strong>${formatPeriod(baristaMonthsToGoal)}</strong>, você poderá trabalhar apenas meio período ganhando ${fmtBR(baristaPartTimeIncome)}/mês.`;
                } else if (baristaProgress >= 100) {
                    baristaPeriod.innerHTML = `<strong>Meta atingida!</strong> Você já pode trabalhar meio período ganhando ${fmtBR(baristaPartTimeIncome)}/mês.`;
                } else {
                    baristaPeriod.textContent = 'Aumente seus aportes para atingir esta meta.';
                }

                // Coast FIRE
                container.querySelector('#coastProgress').textContent = coastFireProgress.toFixed(1) + '%';
                container.querySelector('#coastProgressBar').style.width = Math.min(coastFireProgress, 100) + '%';
                container.querySelector('#coastRequired').textContent = fmtBR(coastFireRequired);
                container.querySelector('#coastGrowth').textContent = fmtBR(coastFireGrowth);
                
                const coastPeriod = container.querySelector('#coastPeriod');
                if (isFinite(coastFireMonthsToGoal) && coastFireMonthsToGoal > 0) {
                    coastPeriod.innerHTML = `Em <strong>${formatPeriod(coastFireMonthsToGoal)}</strong>, você poderá parar de investir e deixar o dinheiro crescer sozinho até os ${retirementAge} anos.`;
                } else if (coastFireProgress >= 100) {
                    coastPeriod.innerHTML = `<strong>Meta atingida!</strong> Você já pode parar de investir e deixar o dinheiro crescer sozinho.`;
                } else {
                    coastPeriod.textContent = 'Aumente seus aportes para atingir esta meta.';
                }

            } catch (e) {
                console.error('❌ Erro no cálculo FIRE:', e.message, e.stack);
                showError(container, 'Erro inesperado nos cálculos. Verifique os valores inseridos.');
            }
        }

        // ===================== INICIALIZAÇÃO =====================

        document.querySelectorAll('.s_fire_calculator').forEach(container => {
            // Event listeners
            container.querySelectorAll('input').forEach(input => {
                input.addEventListener('input', () => {
                    scheduleRecalc(container);
                    saveSettings(container);
                });
                input.addEventListener('change', () => {
                    scheduleRecalc(container);
                    saveSettings(container);
                });
            });

            // Modo real checkbox
            const realModeCheckbox = container.querySelector('#realMode');
            realModeCheckbox.addEventListener('change', function() {
                const label = container.querySelector('#realModeLabel');
                label.textContent = this.checked ? 
                    'Considerar efeito da inflação nos cálculos' : 
                    'Inflação = 0% (valores nominais)';
                scheduleRecalc(container);
                saveSettings(container);
            });

            // Ranges
            container.querySelector('#investmentRange').addEventListener('input', function() {
                container.querySelector('#investmentValue').textContent = parseFloat(this.value).toFixed(1) + '%';
                scheduleRecalc(container);
                saveSettings(container);
            });

            container.querySelector('#expenseIncreaseRange').addEventListener('input', function() {
                const value = parseFloat(this.value);
                const prefix = value > 0 ? '+' : '';
                container.querySelector('#expenseIncreaseValue').textContent = prefix + value.toFixed(1) + '%';
                scheduleRecalc(container);
                saveSettings(container);
            });

            container.querySelector('#withdrawalRateRange').addEventListener('input', function() {
                container.querySelector('#withdrawalRateValue').textContent = parseFloat(this.value).toFixed(1) + '%';
                scheduleRecalc(container);
                saveSettings(container);
            });

            // Carrega configurações salvas ou usa padrões
            const hasSavedSettings = loadSettings(container);
            if (!hasSavedSettings) {
                container.querySelector('#realMode').checked = true;
                container.querySelector('#investmentValue').textContent = '20%';
                container.querySelector('#expenseIncreaseValue').textContent = '0%';
                container.querySelector('#withdrawalRateValue').textContent = '4%';
            }

            // Cálculo inicial
            recalc(container);
        });

        console.log('✅ Calculadora FIRE inicializada com sucesso!');
    }
})();
