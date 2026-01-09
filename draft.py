
    tab_pl, tab_rev, tab_exp, tab_debt = st.tabs(["💰 P&L", "📈 Revenue", "💸 Expenses", "⚠️ Debt"])
    
    with tab_pl:
        st.subheader("Profit & Loss Summary")
        col1, col2 = st.columns(2)
        
        rev_total = rev_filtered['paid'].sum() if not rev_filtered.empty else 0
        exp_total = expenses_filtered['amount'].sum() if not expenses_filtered.empty else 0
        
        # Donut Chart: Revenue vs Expenses
        labels = ['Revenue', 'Expenses']
        values = [rev_total, exp_total]
        fig_donut = px.pie(values=values, names=labels, hole=0.6, color_discrete_sequence=['#00CC96', '#EF553B'])
        col1.plotly_chart(fig_donut, use_container_width=True)
        
        with col2:
            st.metric("Net Profit Margin", f"{((rev_total-exp_total)/rev_total*100):.1f}%" if rev_total > 0 else "0%")
            st.metric("Total Inflow", f"{rev_total:,.0f}")
            st.metric("Total Outflow", f"{exp_total:,.0f}")

    with tab_rev:
        st.subheader("Revenue Analysis")
        if not rev_filtered.empty:
            st.dataframe(rev_filtered.head(5), use_container_width=True)
            daily_trend = rev_filtered.set_index('creation_date').resample('D')['paid'].sum().reset_index()
            fig_rev = px.line(daily_trend, x='creation_date', y='paid', title="Daily Revenue")
            st.plotly_chart(fig_rev, use_container_width=True)

    with tab_exp:
        st.subheader("Expense Breakdown")
        if not expenses_filtered.empty:
            # Assuming expenses has 'category' and 'amount'
            if 'category' in expenses_filtered.columns:
                cat_exp = expenses_filtered.groupby('category')['amount'].sum().reset_index()
                fig_exp = px.bar(cat_exp, x='amount', y='category', orientation='h', color='amount')
                st.plotly_chart(fig_exp, use_container_width=True)
            st.dataframe(expenses_filtered, use_container_width=True)
        else:
            st.info("ℹ️ No expenses data available yet. Ensure 'expenses.csv' is in the processed folder.")
